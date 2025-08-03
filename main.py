from fastapi import FastAPI, HTTPException, Query
from models import CreateTodo, ReturnTodo
from typing import Optional
from databases import Database
from contextlib import asynccontextmanager
from datetime import datetime, date
import pytz
from collections import Counter

DATABASE_URL = "mysql+asyncmy://root:Petuxovyar2006_@localhost:3306/todo"
database = Database(DATABASE_URL)



@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)



@app.post('/create_todo', response_model=ReturnTodo)
async def create_todo(todo: CreateTodo):
    if not todo:
        raise HTTPException(status_code=400, detail='bad request')
    

    query = """insert into todos(title, description) values
    (:title, :description)
    """
    try:
        last_row_id = await database.execute(query=query, values=todo.model_dump())

        select_query = "SELECT * FROM todos WHERE id = :id"

        return_todo = await database.fetch_one(query=select_query, values={"id": last_row_id})

        if not return_todo:
            raise HTTPException(status_code=404, detail="Todo not found after creation")

        return return_todo
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания пользователя: {str(e)}"
        )
    


@app.get('/todos', response_model=list[ReturnTodo])
async def get_todos(
    limit: Optional[int] = Query(10, le=100, ge=0, description='limit of items in query'),
    offset: Optional[int] = Query(0, ge=0),
    sort_by: Optional[str] = Query(None),
    completed: Optional[bool] = Query(None),
    created_after: Optional[date] = Query(None, description="YYYY-MM-DD"),
    created_before: Optional[date] = Query(None, description="YYYY-MM-DD"),
    title_contains: Optional[str] = Query(None)
):
    try:
        query = "SELECT * FROM todos"
        fl = False
        conditionals = ''
        values = {}

        if completed is not None:
            fl = True

            if len(conditionals) == 0:
                conditionals += ' completed = :completed'
            else:
                conditionals += ' AND completed = :completed'

            values['completed'] = completed


        if created_after is not None:
            fl = True

            if len(conditionals) == 0:
                conditionals += ' created_at > :created_after'
            else:
                conditionals += ' AND created_at > :created_after'

            values['created_after'] = created_after

        if created_before is not None:
            fl = True

            if len(conditionals) == 0:
                conditionals += ' created_at < :created_before'
            else:
                conditionals += ' AND created_at < :created_before'

            values['created_before'] = created_before
        
        if title_contains is not None:
            fl = True
            
            if len(conditionals) == 0:
                conditionals += ' LOWER(title) LIKE LOWER(:title_contains)'
            else:
                conditionals += ' AND LOWER(title) LIKE LOWER(:title_contains)'

            values['title_contains'] = f'{title_contains}%'
        

        if fl:
            query += f' WHERE{conditionals}'

        if sort_by is not None:
            # Проверка безопасности
            allowed_sort_fields = ['id', 'title', 'created_at', 'completed']
            sort_field = sort_by.lstrip('-')
            
            if sort_field not in allowed_sort_fields:
                raise HTTPException(status_code=400, detail="Invalid sort field")
            
            direction = 'DESC' if sort_by.startswith('-') else 'ASC'
            query += f' ORDER BY {sort_field} {direction}'

        query += ' LIMIT :limit OFFSET :offset'
        values['limit'] = limit
        values['offset'] = offset

        res = await database.fetch_all(query=query, values=values)


        return res
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid Query')


@app.get('/todos/analytics')
async def get_analytics(timezone: str = Query(..., description='TimeZone (Europe/Moscow)')):
    res = {}
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timezone: {timezone}"
        )
    
    count_query = 'SELECT COUNT(*) as total FROM todos'
    count_todos = await database.fetch_one(query=count_query)

    completed_stats_query_true = 'SELECT COUNT(*) as true_count FROM todos WHERE completed = 1'
    completed_stats_query_false = 'SELECT COUNT(*) as false_count FROM todos WHERE completed = 0'

    count_todos_completed_true = await database.fetch_one(query=completed_stats_query_true)
    count_todos_completed_false = await database.fetch_one(query=completed_stats_query_false)

    avg_completion_time_hours_query = 'SELECT AVG(TIMESTAMPDIFF(SECOND, created_at, completed_at) / 3600) as avg_time FROM todos WHERE completed = 1 AND completed_at IS NOT NULL'    
    avg_time_res = await database.fetch_one(query=avg_completion_time_hours_query)


    query = 'SELECT created_at FROM todos'
    rows = await database.fetch_all(query)

    # Названия дней недели в правильном порядке
    weekdays = [
        "Monday", "Tuesday", "Wednesday", "Thursday", 
        "Friday", "Saturday", "Sunday"
    ]

    # Если нет записей, возвращаем нули
    if not rows:
        return {"weekday_distribution": {day: 0 for day in weekdays}}

    # Считаем количество задач по дням недели
    weekday_counts = Counter()

    for row in rows:
        dt: datetime = row["created_at"]

        # Убедимся, что datetime имеет информацию о таймзоне
        if dt.tzinfo is None:
            # Если время не имеет таймзоны, считаем его UTC
            dt = pytz.UTC.localize(dt)
        
        # Конвертируем в указанную таймзону
        dt_local = dt.astimezone(tz)
        
        # Получаем день недели (0 = понедельник, 6 = воскресенье)
        weekday_idx = dt_local.weekday()
        weekday_name = weekdays[weekday_idx]
        weekday_counts[weekday_name] += 1

    # Формируем финальный ответ
    result = {day: weekday_counts[day] for day in weekdays}

    res['total'] = count_todos['total']
    res['completed_stats'] = {'true': count_todos_completed_true['true_count'], 'false': count_todos_completed_false['false_count']}
    res['avg_completion_time_hours'] = avg_time_res['avg_time']
    res["weekday_distribution"] = result

    return res



@app.patch('/todos')
async def patch_todos(ids: str = Query(..., description='Example: 1,2,3'), completed: bool = Query(..., description='True/False')):
    try:
        get_id_query = 'select id from todos'

        rows = await database.fetch_all(query=get_id_query)

        ids_db = [row['id'] for row in rows]
        ids_query = list(map(int, ids.split(',')))

        res_id_query = [id for id in ids_query if id in ids_db]

        if not res_id_query:
            return {'updated_count': 0}
        
        placeholders = ','.join(f':id_{i}' for i in res_id_query)
        change_status_query = f"""
            UPDATE todos SET completed = :completed WHERE id IN ({placeholders})"""
        
            # Исправлено: передаем словарь, а не список
        update_values = {}

        update_values['completed'] = completed
        for i in res_id_query:
            update_values[f'id_{i}'] = i
        


        await database.execute(query=change_status_query, values=update_values)

        return {'updated_count': len(res_id_query)}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request {e}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)
