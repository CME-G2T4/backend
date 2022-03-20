drop database if exists shinobilorry;
create database shinobilorry;
use shinobilorry;

CREATE TABLE ORDER
(
    orderID int AUTO_INCREMENT,
    customerName varchar(100) not null,
    orderAddress varchar(100) not null,
    orderDateTime datetime not null,
    orderDetail varchar(200) not null,
    trackingNum int not null,
    orderStatus varchar(50) not null,
    deliveryDate datetime not null,

    CONSTRAINT ORDER_PK PRIMARY KEY (orderID)
);

CREATE TABLE INVENTORY
(
    inventoryID int AUTO_INCREMENT,
    orderID int not null,
    lotNum int not null,

    CONSTRAINT INVENTORY_PK PRIMARY KEY (inventoryID),
    CONSTRAINT INVENTORY_FK FOREIGN KEY (orderID) REFERENCES ORDER (orderID)
);

CREATE TABLE FULFILMENT
(
  fulfilmentID int AUTO_INCREMENT,
  orderID int not null,
  driverID int not null,
 
  CONSTRAINT FULFILMENT_PK PRIMARY KEY (fulfilmentID),
  CONSTRAINT FULFILMENT_FK FOREIGN KEY (orderID) REFERENCES ORDER (orderID)

);