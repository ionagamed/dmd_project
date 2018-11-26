DROP TABLE IF EXISTS provider_provides_part_type;
DROP TABLE IF EXISTS part_providers;
DROP TABLE IF EXISTS workshop_has_car_part;
DROP TABLE IF EXISTS car_parts;
DROP TABLE IF EXISTS repairs;
DROP TABLE IF EXISTS workshops;
DROP TABLE IF EXISTS car_part_type_can_be_installed_on_car;
DROP TABLE IF EXISTS car_part_types;
DROP TABLE IF EXISTS socket_occupations;
DROP TABLE IF EXISTS charging_sockets;
DROP TABLE IF EXISTS charging_stations;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS cars;
DROP TABLE IF EXISTS car_models;

CREATE TABLE IF NOT EXISTS car_models (
  id SERIAL PRIMARY KEY,
  model VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS cars (
  id SERIAL PRIMARY KEY,
  color VARCHAR(32) NOT NULL,
  lat FLOAT NOT NULL,
  long FLOAT NOT NULL,
  plate_no VARCHAR(32) NOT NULL,
  type_id INTEGER REFERENCES car_models (id) ON DELETE CASCADE NOT NULL,
  current_charge_percent FLOAT NOT NULL DEFAULT 0,
  joined_company_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  surname VARCHAR(128) NOT NULL,
  phone_number VARCHAR(128) NOT NULL,
  email VARCHAR(128) NOT NULL,
  address VARCHAR(128) NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER REFERENCES customers (id) ON DELETE RESTRICT NOT NULL,
  car_id INTEGER REFERENCES cars (id) ON DELETE RESTRICT NOT NULL,

  car_lat FLOAT NOT NULL,  -- where the car was when the order was placed
  car_long FLOAT NOT NULL,

  pickup_lat FLOAT NOT NULL,
  pickup_long FLOAT NOT NULL,
  dest_lat FLOAT NOT NULL,  -- destination latitude
  dest_long FLOAT NOT NULL,  -- destination longitude

  pickup_time TIMESTAMP NOT NULL,
  finish_time TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL,

  price DECIMAL(20, 2) NOT NULL
);
CREATE TABLE IF NOT EXISTS payments (
  order_id INTEGER PRIMARY KEY REFERENCES orders (id) ON DELETE RESTRICT NOT NULL,
  paid_at TIMESTAMP NOT NULL

  -- a unique constraint for order_id would be nice
  -- but there is a query which assumes that
  -- we don't have it
);
CREATE TABLE IF NOT EXISTS charging_stations (
  id SERIAL PRIMARY KEY,
  lat FLOAT NOT NULL,
  long FLOAT NOT NULL,
  price_per_minute FLOAT NOT NULL
);
CREATE TABLE IF NOT EXISTS charging_sockets (
  id SERIAL PRIMARY KEY,
  shape VARCHAR(64) NOT NULL,
  size FLOAT NOT NULL,
  station_id INTEGER REFERENCES charging_stations (id) ON DELETE CASCADE NOT NULL
);
CREATE TABLE IF NOT EXISTS socket_occupations (
  id SERIAL PRIMARY KEY,
  socket_id INTEGER REFERENCES charging_sockets (id) ON DELETE CASCADE NOT NULL,
  car_id INTEGER REFERENCES cars (id) ON DELETE CASCADE NOT NULL,
  time_begin TIMESTAMP NOT NULL,
  time_end TIMESTAMP
);
CREATE TABLE IF NOT EXISTS car_part_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS car_part_type_can_be_installed_on_car (
  car_id INTEGER REFERENCES cars (id) ON DELETE CASCADE NOT NULL,
  part_id INTEGER REFERENCES car_part_types (id) ON DELETE CASCADE NOT NULL,
  PRIMARY KEY (car_id, part_id)
);
CREATE TABLE IF NOT EXISTS workshops (
  id SERIAL PRIMARY KEY,
  lat FLOAT NOT NULL,
  long FLOAT NOT NULL
);
CREATE TABLE IF NOT EXISTS repairs (
  id SERIAL PRIMARY KEY,
  car_id INTEGER REFERENCES cars (id) ON DELETE CASCADE NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  workshop_id INTEGER REFERENCES workshops (id) ON DELETE CASCADE NOT NULL
);
CREATE TABLE IF NOT EXISTS car_parts (
  id SERIAL PRIMARY KEY,
  type_id INTEGER REFERENCES car_part_types (id) ON DELETE CASCADE NOT NULL,
  price DECIMAL(20, 2) NOT NULL,
  involved_in_repair_id INTEGER REFERENCES repairs (id) ON DELETE CASCADE NULL
);
CREATE TABLE IF NOT EXISTS workshop_has_car_part (
  workshop_id INTEGER REFERENCES workshops (id) ON DELETE CASCADE NOT NULL,
  part_id INTEGER REFERENCES car_parts (id) ON DELETE CASCADE NOT NULL,
  PRIMARY KEY (workshop_id, part_id)
);
CREATE TABLE IF NOT EXISTS part_providers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  lat FLOAT NOT NULL,
  long FLOAT NOT NULL,
  phone VARCHAR(64) NOT NULL
);
CREATE TABLE IF NOT EXISTS provider_provides_part_type (
  provider_id INTEGER REFERENCES part_providers (id) ON DELETE CASCADE NOT NULL,
  part_type_id INTEGER REFERENCES car_part_types (id) ON DELETE CASCADE NOT NULL,
  PRIMARY KEY (provider_id, part_type_id)
);


INSERT INTO car_models (model) VALUES
  ('Tesla Model S'),
  ('Tesla Model M');
INSERT INTO cars (color, lat, long, plate_no, type_id, joined_company_at) VALUES
  ('red', 1, 2, 'AN512B', 1, timestamp '2018-10-01 00:00'),
  ('green', 3, 4, 'RU222S', 1, timestamp '2018-10-01 00:00'),
  ('red', 5, 6, 'asdf11', 2, timestamp '2018-10-01 00:00'),
  ('blue', 7, 8, 'PP567FF', 2, timestamp '2018-10-01 00:00');
INSERT INTO customers (name, surname, phone_number, email, address) VALUES
  ('Vasiliy', 'Pupkin', '123', 'v.pupkin@localhost', 'Sample st. 1'),
  ('John', 'Doe', '113', 'j.doe@localhost', 'Sample st. 2'),
  ('Jane', 'Doe', '114', 'j.doe@gmail.com', 'Sample st. 2');
INSERT INTO orders (customer_id, car_id, car_lat, car_long, pickup_lat, pickup_long, dest_lat, dest_long, created_at, pickup_time, finish_time, price) VALUES
  (1, 2, 7, 6, 10, 10, 15, 15, timestamp '2018-11-10 09:50', timestamp '2018-11-10 10:00', timestamp '2018-11-10 10:08', 100),
  (1, 1, -2, 5, 10, 10, 15, 15, timestamp '2018-11-11 09:50', timestamp '2018-11-11 10:00', timestamp '2018-11-11 10:08', 100),
  (2, 2, 7, 6, 100, 10, 15, 15, timestamp '2018-11-10 12:50', timestamp '2018-11-10 13:00', timestamp '2018-11-10 13:08', 100),
  (1, 3, -2, 5, 100, 10, 15, 15, timestamp '2018-11-12 09:50', timestamp '2018-11-12 10:00', timestamp '2018-11-12 10:08', 100),
  (3, 2, 7, 6, 10, 10, 15, 15, timestamp '2018-11-10 16:50', timestamp '2018-11-10 17:00', timestamp '2018-11-10 17:08', 100),
  (2, 1, -2, 5, 0, 10, 15, 15, timestamp '2018-11-10 09:50', timestamp '2018-11-10 10:00', timestamp '2018-11-10 10:08', 100),
  (1, 2, 7, 6, 180, 10, 15, 15, timestamp '2018-11-10 17:50', timestamp '2018-11-10 18:00', timestamp '2018-11-10 18:08', 100),
  (1, 4, -2, 5, 110, 10, 15, 15, timestamp '2018-11-13 09:50', timestamp '2018-11-13 10:00', timestamp '2018-11-13 10:08', 100);
INSERT INTO payments (order_id, paid_at) VALUES
  (1, now()),
  (2, now()),
  (3, now()),
  (4, now()),
  (5, now()),
  (6, now()),
  (7, now()),
  (8, now());
INSERT INTO charging_stations (lat, long, price_per_minute) VALUES
  (100, 100, 10),
  (0, 0, 15);
INSERT INTO charging_sockets (shape, size, station_id) VALUES
  ('square', 10, 1),
  ('circle', 3, 1),
  ('square', 5, 2),
  ('triangle', 6, 2);
INSERT INTO socket_occupations (socket_id, car_id, time_begin, time_end) VALUES
  (1, 1, timestamp '2018-11-10 11:00', timestamp '2018-11-10 11:15'),
  (1, 1, timestamp '2018-11-10 19:00', timestamp '2018-11-10 19:20');
INSERT INTO workshops (lat, long) VALUES
  (1000, 1000),
  (1001, 1000);
INSERT INTO car_part_types (name) VALUES
  ('windshield washer motor'),
  ('sparking cable');
INSERT INTO repairs (car_id, timestamp, workshop_id) VALUES
  (1, timestamp '2018-10-10 20:00', 1),
  (1, timestamp '2018-10-18 20:00', 1),
  (2, timestamp '2018-10-14 20:00', 2),
  (2, timestamp '2018-10-13 23:00', 1),
  (2, timestamp '2018-10-13 21:00', 1),
  (2, timestamp '2018-10-13 19:00', 1),
  (1, timestamp '2018-10-24 21:00', 2);
INSERT INTO car_parts (type_id, price, involved_in_repair_id) VALUES
  (1, 100, 1),
  (1, 150, 2),
  (2, 300, 3),
  (2, 400, 4),
  (2, 400, 5),
  (2, 350, 6),
  (2, 375, 7);

