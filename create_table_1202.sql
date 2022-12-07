create table Airline
	(airline_name	varchar(20),
	 primary key (airline_name)
	);

create table Airline_Staff
    (staff_user_name      varchar(20),
     staff_password       varchar(20) not null,
     staff_first_name     varchar(20) not null,
     staff_last_name      varchar(20) not null,
     staff_date_of_birth  date not null,
     airline_name         varchar(20),
     primary key (staff_user_name),
     foreign key (airline_name) references Airline(airline_name)
        on delete set null
    );

create table Permission
    (staff_user_name	varchar(20) not null,
     permission_name    varchar(10) check (permission_name = 'Admin' or permission_name = 'Operator'),
	 primary key (staff_user_name, permission_name),
     foreign key (staff_user_name) references Airline_Staff(staff_user_name)
        on delete cascade
	);

create table Airport
    (airport_name	varchar(5),
     airport_city   varchar(15) not null,
	 primary key (airport_name)
	);

create table Airplane
    (airplane_id    varchar(10) not null,
     airline_name   varchar(20) not null,
     seats      int(11) not null,
     primary key(airplane_id, airline_name),
     foreign key (airline_name) references Airline(airline_name)
        on delete cascade
    );

create table Flight
    (airline_name   varchar(20) not null,
     flight_num     varchar(10) not null,
     departure_time datetime NOT NULL,
     arrival_time   datetime NOT NULL,
     price          numeric(6,0) not null,
     status         varchar(20) not null,
     arrival_airport_name   varchar(5),
     departure_airport_name varchar(5),
     airplane_id    varchar(10),
     primary key (airline_name, flight_num),
     foreign key (airline_name) references Airline(airline_name)
        on delete cascade,
     foreign key (arrival_airport_name) references Airport(airport_name)
        on delete set null,
     foreign key (departure_airport_name) references Airport(airport_name)
        on delete set null,
     foreign key (airplane_id) references Airplane(airplane_id)
        on delete set null
    );

create table Booking_Agent
    (booking_agent_email        varchar(20) not null,
     booking_agent_password     varchar(20) not null,
     booking_agent_id           varchar(20) not null,
     primary key (booking_agent_email)
    );

create table Customer
    (customer_email     varchar(20) not null,
     customer_name      varchar(20) not null,
     customer_password  varchar(20) not null,
     building_number    varchar(7) not null,
     street             varchar(30) not null,
     city               varchar(15) not null,
     state              varchar(15) not null,
     phone_number       varchar(15) not null,
     passport_number    varchar(15) not null,
     passport_expiration    date not null,
     passprt_country    varchar(15) not null,
     customer_date_of_birth date not null,
     primary key (customer_email)
    );

create table Ticket
    (ticket_id      (20),
     airline_name   varchar(20),
     flight_num     varchar(10),
     customer_email varchar(20),
     booking_agent_email varchar(20),
     purchase_date date,
     primary key (ticket_id),
     foreign key (airline_name, flight_num) references Flight(airline_name, flight_num)
        on delete set null,
     foreign key (customer_email) references Customer(customer_email)
        on delete set null,
     foreign key (booking_agent_email) references Booking_Agent(booking_agent_email)
        on delete set null
    );

create table Works_for(
    airline_name varchar(20),
    booking_agent_email varchar(20),
    primary key (airline_name, booking_agent_email),
	foreign key (airline_name) references Airline(airline_name),
    foreign key (booking_agent_email) references Booking_Agent(booking_agent_email));
