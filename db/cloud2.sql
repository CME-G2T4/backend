drop database if exists shinobilorry;
create database shinobilorry;
use shinobilorry;

CREATE TABLE ORDERS
(
    orderID int AUTO_INCREMENT,
    customer_name varchar(100) not null,
    order_address varchar(200) not null,
    order_datetime datetime not null,
    tracking_no int not null,
    order_status varchar(50) not null,
    order_details varchar(200) not null,
    deliver_date datetime not null,

    CONSTRAINT ORDER_PK PRIMARY KEY (order_id)
);

CREATE TABLE INVENTORY
(
    inventory_id int AUTO_INCREMENT,
    order_id int not null,
    lot_num int not null,

    CONSTRAINT INVENTORY_PK PRIMARY KEY (inventory_id),
    CONSTRAINT INVENTORY_FK FOREIGN KEY (order_id) REFERENCES ORDER (order_id)
);

CREATE TABLE FULFILMENT
(
  fulfilment_id int AUTO_INCREMENT,
  order_id int not null,
  driver_id int not null,
 
  CONSTRAINT FULFILMENT_PK PRIMARY KEY (fulfilment_id),
  CONSTRAINT FULFILMENT_FK FOREIGN KEY (order_id) REFERENCES ORDER (order_id)

);