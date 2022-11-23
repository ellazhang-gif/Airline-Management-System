insert into Airline 
values ("China Eastern"), ("Emirates");

insert into Airport 
values ("JFK","NYC"), ("PVG","Shanghai");

insert into Customer
values ("ymz213@nyu.edu","Ella Zhang", "12801002myz", "1555", "Century Avenue", "Shanghai", "Shanghai", "15004512996", "EH9977064", "2031-4-12", "China", "2001-8-21"), ("3345055209@qq.com", "Yimeng Zhang", "12801002myz", "895", "Pusan Road", "Shanghai", "Shanghai", "18521040578", "EH9977065", "2032-4-12", "China", "2001-9-15");

insert into Booking_Agent
values ("xd652@nyu.edu","xd652", "00001");

insert into Airplane
values ("China Eastern", 1, 200), ("China Eastern", 2, 202), ("Emirates", 11,400), ("Emirates", 12, 402);

insert into Airline_Staff
values ("staff001", "9876543", "Andy", "Zhang", "1999-1-1", "China Eastern");

insert into Flight
values ("China Eastern",625, "JFK", "2022-10-23 06:00:30.75", "PVG", "2022-10-23 20:00:30.99", 4999, "in-progress", 1),
		("China Eastern",625, "PVG", "2022-10-24 06:00:30.75", "JFK", "2022-10-24 20:00:30.99", 4999, "upcoming", 1),
        ("China Eastern",627, "PVG", "2022-10-22 23:00:30.75", "JFK", "2022-10-23 15:00:30.99", 4999, "delayed", 2);

insert into Ticket
values (10101,"China Eastern", 625),
		(10102,"China Eastern", 627);
