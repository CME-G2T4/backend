drop database if exists shinobilorry;
create database shinobilorry;
use shinobilorry;

CREATE TABLE ORDERS
(
    order_id int AUTO_INCREMENT,
    customer_name varchar(255) not null,
    order_address varchar(255) not null,
    order_datetime datetime not null,
    tracking_no int not null,
    order_status varchar(50) not null,
    order_details varchar(255) not null,
    delivery_date datetime not null,

    CONSTRAINT ORDERS_PK PRIMARY KEY (order_id)
);

CREATE TABLE INVENTORY
(
    inventory_id int AUTO_INCREMENT,
    order_id int not null,
    lot_num int not null,

    CONSTRAINT INVENTORY_PK PRIMARY KEY (inventory_id)
);

CREATE TABLE FULFILMENT
(
  fulfilment_id int AUTO_INCREMENT,
  order_id int not null,
  driver_id int not null,
  delivery_date datetime not null,
  order_address varchar(255) not null,

  CONSTRAINT FULFILMENT_PK PRIMARY KEY (fulfilment_id)
);