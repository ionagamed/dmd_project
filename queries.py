"""
This file was written before the dmd_project requirement
so, sorry for the code style (sql should be readable though)
"""

import sys
import os
from collections import defaultdict
from dateutil.parser import parse as parse_datetime
import psycopg2
import psycopg2.extras


def connect_to_db():
    db_port = int(os.environ.get('DB_PORT', 6060))
    db_host = os.environ.get('DB_HOST', 'localhost')

    connection = psycopg2.connect(
        'dbname=dmd_project '
        'user=dmd_project '
        f'host={db_host} '
        f'port={db_port} '
        'password=dmd_project'
    )
    return connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)


def query_1():
    cur = connect_to_db()
    source = 'SELECT * FROM cars WHERE plate_no LIKE %s AND color=%s'
    cur.execute(
        source,
        ('AN%', 'red')
    )
    rows = cur.fetchall()
    return rows, source


def query_2(date):
    # only using time_begin, as i couldn't grasp how to do it
    # using GROUP BY and both time_begin and time_end
    # without python in raw SQL

    date = parse_datetime(date).date()
    cur = connect_to_db()
    cur.execute('''
        SELECT 
          EXTRACT(HOUR FROM time_begin) AS hour,
          COUNT(socket_id) 
        FROM socket_occupations
        WHERE time_begin::DATE=%s
        GROUP BY (hour)
    ''', (date,))
    rows = cur.fetchall()
    table = defaultdict(int)
    for row in rows:
        table[int(row.hour)] = row.count
    print('+----------------+')
    for hour in range(0, 23):
        begin = str(hour).zfill(2)
        end = str(hour).zfill(2)
        count = str(table[hour]).rjust(4)
        print(f'| {begin}h-{end}h | {count} |')
    print('+----------------+')


def query_3():
    cur = connect_to_db()
    cur.execute('''
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
    ''')
    row = cur.fetchone()
    print(f'Morning: {row.morning_count}%')
    print(f'Afternoon: {row.afternoon_count}%')
    print(f'Evening: {row.evening_count}%')


def query_4(customer_id):
    cur = connect_to_db()
    cur.execute('''
        SELECT order_id, COUNT(order_id) FROM payments 
          JOIN orders ON payments.order_id = orders.id
          WHERE customer_id=%s 
                AND pickup_time > now() - INTERVAL '1 month'
          GROUP BY order_id
          HAVING COUNT(order_id) > 1
    ''', (customer_id,))
    rows = cur.fetchall()
    print(rows)


def query_5(date):
    date = parse_datetime(date).date()
    cur = connect_to_db()
    cur.execute('''
        SELECT 
          AVG(finish_time - pickup_time) AS avg_trip, 
          AVG(|/
            (car_lat - pickup_lat) ^ 2 +
            (car_long - pickup_long) ^ 2
          ) AS avg_init
        FROM orders
        WHERE created_at::DATE=%s;
    ''', (date,))
    rows = cur.fetchone()
    print(f'Average trip duration: {rows.avg_trip}')
    print(f'Average car current-to-pickup travel distance: {rows.avg_init}')


def query_6():
    cur = connect_to_db()
    cur.execute('''
        SELECT pickup_lat, pickup_long, COUNT(*) AS cnt
        FROM orders
        WHERE
          EXTRACT(HOUR FROM orders.created_at) >= 7 AND
          EXTRACT(HOUR FROM orders.created_at) <= 10
        GROUP BY (pickup_lat, pickup_long)
        ORDER BY cnt DESC
        LIMIT 3
    ''')
    morning_pickup_top = cur.fetchall()
    cur.execute('''
        SELECT pickup_lat, pickup_long, COUNT(*) AS cnt
        FROM orders
        WHERE
          EXTRACT(HOUR FROM orders.created_at) >= 12 AND
          EXTRACT(HOUR FROM orders.created_at) <= 14
        GROUP BY (pickup_lat, pickup_long)
        ORDER BY cnt DESC
        LIMIT 3
    ''')
    afternoon_pickup_top = cur.fetchall()
    cur.execute('''
        SELECT pickup_lat, pickup_long, COUNT(*) as cnt
        FROM orders
        WHERE
          EXTRACT(HOUR FROM orders.created_at) >= 17 AND
          EXTRACT(HOUR FROM orders.created_at) <= 19
        GROUP BY (pickup_lat, pickup_long)
        ORDER BY cnt DESC
        LIMIT 3
    ''')
    evening_pickup_top = cur.fetchall()
    cur.execute('''
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
    morning_distance_top = cur.fetchall()
    cur.execute('''
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
    afternoon_distance_top = cur.fetchall()
    cur.execute('''
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
    evening_distance_top = cur.fetchall()

    print('Top 3 pick-up locations:')
    print(' | Morning (7:00 - 10:00):')
    for entry in morning_pickup_top:
        print(f' |  | ({entry.pickup_lat}, {entry.pickup_long}) - {entry.cnt} times')
    print(' | Afternoon (12:00 - 14:00):')
    for entry in afternoon_pickup_top:
        print(f' |  | ({entry.pickup_lat}, {entry.pickup_long}) - {entry.cnt} times')
    print(' | Evening (17:00 - 19:00):')
    for entry in evening_pickup_top:
        print(f' |  | ({entry.pickup_lat}, {entry.pickup_long}) - {entry.cnt} times')
    print('Top 3 distances:')
    print(' | Morning (7:00 - 10:00):')
    for entry in morning_distance_top:
        print(f' |  | {entry.distance}km - {entry.cnt} times')
    print(' | Afternoon (12:00 - 14:00):')
    for entry in afternoon_distance_top:
        print(f' |  | {entry.distance}km - {entry.cnt} times')
    print(' | Evening (17:00 - 19:00):')
    for entry in evening_distance_top:
        print(f' |  | {entry.distance}km - {entry.cnt} times')


def query_7():
    cur = connect_to_db()
    cur.execute('''
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
    ''')
    rows = cur.fetchall()
    print(f'Bad cars: {rows}')


def query_8(start_date):
    start_date = parse_datetime(start_date).date()
    cur = connect_to_db()
    cur.execute('''
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
    ''', (start_date, start_date,))
    rows = cur.fetchall()
    for i in rows:
        print(f'Customer with id {i.customer_id} caused {i.amount} charge events')


def query_9():
    cur = connect_to_db()
    cur.execute('''
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
    ''')
    rows = cur.fetchall()
    used_workshop_ids = set()
    entries = []
    for row in rows:
        if row.workshop_id not in used_workshop_ids:
            used_workshop_ids.add(row.workshop_id)
            entries.append(row)
    for entry in entries:
        print(f'Workshop with id {entry.workshop_id} most often requires "{entry.car_part_name}" (about {int(entry.avg_per_week)} every week on average)')


def query_10():
    # considering that we need to count from the
    # time when the car appeared, not only days it was being repaired
    # at least once (which was my first thought)

    cur = connect_to_db()
    cur.execute('''
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
    ''')
    row = cur.fetchone()
    print(f'The most costly car has id {row.car_id} and costs {row.car_cost} a day average')


def execute_query(n, *args):
    return globals()['query_' + str(int(n))](*args)


def main():
    qn = sys.argv[1]
    args = sys.argv[2:]
    execute_query(qn, *args)


if __name__ == '__main__':
    main()
