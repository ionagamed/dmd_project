from dmd_project.models.db import connect_to_db
from dmd_project.models.utils import QueryResult, wrap


def customer_choices():
    db = connect_to_db()
    db.execute('SELECT id, name, surname, email FROM customers')
    return [
        {
            'id': str(x[0]),
            'text': f'{x[1]} {x[2]} – {x[3]}'
        } for x in db.fetchall()
    ]


def query_1():
    db = connect_to_db()
    source = 'SELECT * FROM cars WHERE plate_no LIKE \'AN%\' AND color=\'red\''
    db.execute(source)
    return QueryResult(db, source)


@wrap
def query_2(date):
    db = connect_to_db()
    source = '''
SELECT 
  EXTRACT(HOUR FROM time_begin) AS hour,
  COUNT(socket_id) 
FROM socket_occupations
WHERE time_begin::DATE=%s
GROUP BY (hour)
    '''
    db.execute(source, [date])
    return QueryResult(db, source)


def query_3():
    db = connect_to_db()
    source = '''
SELECT 
  COUNT(
    DISTINCT
    CASE WHEN 
      EXTRACT(HOUR FROM orders.created_at) >= 7 AND
      EXTRACT(HOUR FROM orders.created_at) <= 10
    THEN
      car_id
    ELSE
      NULL
    END
  )::FLOAT / (SELECT COUNT(*) FROM cars) * 100
   AS morning_count,
  
  COUNT(
    DISTINCT
    CASE WHEN 
      EXTRACT(HOUR FROM orders.created_at) >= 12 AND
      EXTRACT(HOUR FROM orders.created_at) <= 14
    THEN
      car_id
    ELSE
      NULL
    END
  )::FLOAT / (SELECT COUNT(*) FROM cars) * 100
   AS afternoon_count,
   
  COUNT(
    DISTINCT
    CASE WHEN 
      EXTRACT(HOUR FROM orders.created_at) >= 17 AND
      EXTRACT(HOUR FROM orders.created_at) <= 19
    THEN
      car_id
    ELSE
      NULL
    END
  )::FLOAT / (SELECT COUNT(*) FROM cars) * 100
   AS evening_count
FROM orders
WHERE
  orders.created_at::DATE < now() AND
  orders.created_at::DATE > now() - INTERVAL '1 week'
    '''
    db.execute(source)
    return QueryResult(db, source)


@wrap
def query_4(customer_id):
    db = connect_to_db()
    source = '''
SELECT order_id, COUNT(order_id) FROM payments 
JOIN orders ON payments.order_id = orders.id
WHERE customer_id=%s 
    AND pickup_time > now() - INTERVAL '1 month'
GROUP BY order_id
    '''
    db.execute(source, [customer_id])
    return QueryResult(db, source)


@wrap
def query_5(date):
    db = connect_to_db()
    source = '''
SELECT 
  AVG(finish_time - pickup_time) AS avg_trip, 
  AVG(|/
    (car_lat - pickup_lat) ^ 2 +
    (car_long - pickup_long) ^ 2
  ) AS avg_dist
FROM orders
WHERE created_at::DATE=%s;
    '''
    db.execute(source, [date])
    return QueryResult(db, source)


def query_6():
    db = connect_to_db()
    sources = []
    sources.append('''
            SELECT pickup_lat, pickup_long, COUNT(*) AS cnt
            FROM orders
            WHERE
              EXTRACT(HOUR FROM orders.created_at) >= 7 AND
              EXTRACT(HOUR FROM orders.created_at) <= 10
            GROUP BY (pickup_lat, pickup_long)
            ORDER BY cnt DESC
            LIMIT 3
        ''')
    db.execute(sources[-1])
    morning_pickup_top = db.fetchall()
    sources.append('''
            SELECT pickup_lat, pickup_long, COUNT(*) AS cnt
            FROM orders
            WHERE
              EXTRACT(HOUR FROM orders.created_at) >= 12 AND
              EXTRACT(HOUR FROM orders.created_at) <= 14
            GROUP BY (pickup_lat, pickup_long)
            ORDER BY cnt DESC
            LIMIT 3
        ''')
    db.execute(sources[-1])
    afternoon_pickup_top = db.fetchall()
    sources.append('''
            SELECT pickup_lat, pickup_long, COUNT(*) as cnt
            FROM orders
            WHERE
              EXTRACT(HOUR FROM orders.created_at) >= 17 AND
              EXTRACT(HOUR FROM orders.created_at) <= 19
            GROUP BY (pickup_lat, pickup_long)
            ORDER BY cnt DESC
            LIMIT 3
        ''')
    db.execute(sources[-1])
    evening_pickup_top = db.fetchall()
    sources.append('''
            SELECT 
              |/ ((pickup_lat - dest_lat) ^ 2 + (pickup_long - dest_long) ^ 2) AS distance, 
              COUNT(*) as cnt
            FROM orders
            WHERE
              EXTRACT(HOUR FROM orders.created_at) >= 7 AND
              EXTRACT(HOUR FROM orders.created_at) <= 10
            GROUP BY distance
            ORDER BY cnt DESC
            LIMIT 3
        ''')
    db.execute(sources[-1])
    morning_distance_top = db.fetchall()
    sources.append('''
            SELECT 
              |/ ((pickup_lat - dest_lat) ^ 2 + (pickup_long - dest_long) ^ 2) AS distance, 
              COUNT(*) as cnt
            FROM orders
            WHERE
              EXTRACT(HOUR FROM orders.created_at) >= 12 AND
              EXTRACT(HOUR FROM orders.created_at) <= 14
            GROUP BY distance
            ORDER BY cnt DESC
            LIMIT 3
        ''')
    db.execute(sources[-1])
    afternoon_distance_top = db.fetchall()
    sources.append('''
            SELECT 
              |/ ((pickup_lat - dest_lat) ^ 2 + (pickup_long - dest_long) ^ 2) AS distance, 
              COUNT(*) as cnt
            FROM orders
            WHERE
              EXTRACT(HOUR FROM orders.created_at) >= 17 AND
              EXTRACT(HOUR FROM orders.created_at) <= 19
            GROUP BY distance
            ORDER BY cnt DESC
            LIMIT 3
        ''')
    db.execute(sources[-1])
    evening_distance_top = db.fetchall()

    headings1 = ('type', 'time_of_day', 'distance', 'cnt')
    data1 = [
        *[('distance', 'morning', x[0], x[1]) for x in morning_distance_top],
        *[('distance', 'afternoon', x[0], x[1]) for x in afternoon_distance_top],
        *[('distance', 'evening', x[0], x[1]) for x in evening_distance_top],
    ]

    headings2 = ('type', 'time_of_day', 'lat', 'long', 'cnt')
    data2 = [
        *[('pickup location', 'morning', x[0], x[1], x[2]) for x in morning_pickup_top],
        *[('pickup location', 'afternoon', x[0], x[1], x[2]) for x in afternoon_pickup_top],
        *[('pickup location', 'evening', x[0], x[1], x[2]) for x in evening_pickup_top],
    ]

    qr1 = QueryResult(None, None)
    qr1.headings = headings1
    qr1.rows = data1
    qr1.source = '\n---------------\n'.join(sources[3:])

    qr2 = QueryResult(None, None)
    qr2.headings = headings2
    qr2.rows = data2
    qr2.source = '\n---------------\n'.join(sources[:3])

    return qr1, qr2


def query_7():
    db = connect_to_db()
    source = '''
SELECT 
  cars.id,
  COUNT(orders.car_id) AS orders_count
FROM cars
JOIN 
  orders ON cars.id = orders.car_id AND 
  orders.created_at > now() - INTERVAL '3 months'
GROUP BY (cars.id)
ORDER BY orders_count
LIMIT (SELECT COUNT(id) / 10.0 FROM cars)
    '''
    db.execute(source)
    return QueryResult(db, source)


@wrap
def query_8(date):
    db = connect_to_db()
    source = '''
SELECT
  customers.id AS customer_id,
  SUM(cnt) AS amount
FROM customers
JOIN (
  SELECT
    customers.id AS customer_id,
    COUNT(*) AS cnt
  FROM customers
  JOIN orders ON customers.id = orders.customer_id 
        AND orders.created_at::date < %s::date + interval '1 month'
        AND orders.created_at::date > %s::date
  JOIN cars ON orders.car_id = cars.id
  JOIN socket_occupations ON cars.id = socket_occupations.car_id 
        AND socket_occupations.time_begin::date = orders.created_at::date
  GROUP BY customers.id
) AS t1 ON t1.customer_id = customers.id
GROUP BY customers.id
    '''
    db.execute(source, [date, date])
    return QueryResult(db, source)


def query_9():
    db = connect_to_db()
    source = '''
SELECT
  workshops.id AS workshop_id,
  car_part_name,
  AVG(per_week_counts) AS avg_per_week
FROM workshops
JOIN (
  SELECT 
    car_part_types.name AS car_part_name,
    COUNT(*) AS per_week_counts,
    repairs.workshop_id
  FROM car_parts
  JOIN repairs ON car_parts.involved_in_repair_id = repairs.id
  JOIN car_part_types ON car_parts.type_id = car_part_types.id
  GROUP BY (car_part_types.name, EXTRACT(WEEK FROM repairs.timestamp), repairs.workshop_id)
) AS counts ON workshop_id = workshops.id
GROUP BY (workshops.id, car_part_name)
ORDER BY avg_per_week DESC
    '''
    db.execute(source)
    return QueryResult(db, source)


def query_10():
    db = connect_to_db()
    source = '''
SELECT
  cars.id as car_id,
  avg_maintenance_cost AS car_cost
FROM cars
JOIN (
  SELECT
    cars.id AS car_id,
    SUM(car_parts.price)::float / (now()::date - cars.joined_company_at::date) 
      AS avg_maintenance_cost
  FROM cars
  JOIN repairs ON cars.id = repairs.car_id
  JOIN car_parts ON repairs.id = car_parts.involved_in_repair_id
  GROUP BY cars.id
) AS maintenance_cost_table ON cars.id = maintenance_cost_table.car_id
LEFT JOIN (
  SELECT
    cars.id AS car_id,
    SUM(
      charging_stations.price_per_minute * 
        EXTRACT(MINUTE FROM (socket_occupations.time_end - socket_occupations.time_begin))
    ) / (now()::date - cars.joined_company_at::date) AS avg_charging_cost
  FROM cars
  JOIN socket_occupations ON cars.id = socket_occupations.car_id
  JOIN charging_sockets ON socket_occupations.socket_id = charging_sockets.id
  JOIN charging_stations ON charging_sockets.station_id = charging_stations.id
  GROUP BY cars.id
) AS charging_cost_table ON cars.id = charging_cost_table.car_id
GROUP BY (cars.id, avg_maintenance_cost)
ORDER BY avg_maintenance_cost DESC
LIMIT 1
    '''
    db.execute(source)
    return QueryResult(db, source)


@wrap
def custom(query):
    db = connect_to_db()
    db.execute(query)
    return QueryResult(db, query)
