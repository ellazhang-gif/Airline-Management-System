insert into Airline values ('China Eastern');
insert into Airline values ('China International Airlines');
insert into Airline values ('Delta Airlines');
insert into Airline values ('American Airlines');
insert into Airline values ('Korean Air');

insert into Airport values ('JFK', 'New York City');
insert into Airport values ('PVG', 'Shanghai');
insert into Airport values ('PEK', 'Beijing');
insert into Airport values ('BOS','Boston');
insert into Airport values ('LAX', 'Los Angeles');
insert into Airport values ('ICN', 'Incheon');

insert into Customer values ('shiyuan123@126.com', 'Shiyuan Liu', 'shiyuan888',
    '1550', 'Century Avenue', 'Shanghai', 'Shanghai', '1501234567', 'EE673521', '2028-08-26',
    'China', '2000-01-01');
insert into Customer values ('xiaoming@163.com', 'Xiaoming Wang', 'xiaoming777',
    '33', 'Apple Street', 'Beijing', 'Beijing', '18667549382', 'EE156382', '2025-03-14',
    'China', '2002-12-10');
insert into Customer values ('amy456@gmail.com', 'Amy Park', 'amygoodgoodstudy',
    '14', '38th Street', 'New York', 'New York', '542375632', 'UT384762', '2022-12-06',
    'US', '1992-08-26');
insert into Customer values ('tom123@gmail.com', 'Tom Green', 'tomisagoodboy', 
    '233', 'Bay State Road', 'Boston', 'Massachusetts', '577826234', 'UT52832','2031-10-10',
    'US', '1989-12-21');
insert into Customer values ('62836192@qq.com', 'Jinyuan Xi', 'jinyuan666',
    '2', 'Fucheng Road', 'Beijing', 'Beijing', '58591587', 'EE01321', '2029-08-01',
    'China', '1973-02-26');
insert into Customer values ('andyzhang@126.com', 'Andy Zhang', 'hahahahaha',
    '11', 'East Ocean Road', 'New York', 'New York', '526192731', 'UT761823', '2025-09-31',
    'US', '1992-03-04');

insert into Booking_Agent values ('citytrip@163.com', 'citytrip134', '034');
insert into Booking_Agent values ('Tuniulvxing@qq.com', 'tuniu888', '145');
insert into Booking_Agent values ('expedia@gmail.com', 'expedia66', '021');
insert into Booking_Agent values ('taobao@126.com', 'taobaohaha', '093');
insert into Booking_Agent values ('thankyoutrip@163.com', 'thankyousir', '372');
insert into Booking_Agent values ('dontknowwhattoadd@qq.com', 'lmao66', '999');

insert into Airplane values ('0935', 'China Eastern', '200');
insert into Airplane values ('4726', 'China International Airline', '200');
insert into Airplane values ('0567', 'Delta Airlines', '150');
insert into Airplane values ('2112', 'China International Airline', '100');
insert into Airplane values ('0098', 'Delta Airlines', '50');
insert into Airplane values ('0542', 'China Eastern', '100');
insert into Airplane values ('1473', 'Korean Air', '100');
insert into Airplane values ('8712', 'American Airlines', '30');
insert into Airplane values ('3333', 'American Airlines', '60');
insert into Airplane values ('6666', 'Korean Air', '200');

insert into Airline_Staff values ('JZHANG564', 'qwerty625', 'Jiashuai', 'Zhang', '1980-09-03', 
    'China Eastern');
insert into Airline_Staff values ('Meili123', '456qrwycn', 'Meili', 'Liu', '1992-12-01',
    'China International Airline');
insert into Airline_Staff values ('wasai66', 'qwerty', 'Waisai', 'Zhang', '1999-08-09',
    'China International Airline');
insert into Airline_Staff values ('Jack456', '3772lalala', 'Jack', 'Ma', '1970-08-26',
    'Delta Airlines');
insert into Airline_Staff values ('Steven88', '99998888', 'Steven', 'James', '1993-04-05',
    'American Airlines');
insert into Airline_Staff values ('Kiko11', 'yyyyzzzz', 'Kiko', 'PG', '1989-12-12',
    'Korean Air');

insert into Permission values ('JZHANG564', 'Operator');
insert into Permission values ('JZHANG564', 'Admin');
insert into Permission values ('Meili123', 'Admin');
insert into Permission values ('wasai66', 'Operator');
insert into Permission values ('Jack456', 'Admin');
insert into Permission values ('Jack456', 'Operator');
insert into Permission values ('Steven88', 'Admin');
insert into Permission values ('Steven88', 'Operator');
insert into Permission values ('Kiko11', 'Admin');
insert into Permission values ('Kiko11', 'Operator');


insert into Flight values ('China Eastern', 'MU588', '2022-12-07 20:00:00', '2022-12-08 09:30:00',
    '18700', 'upcoming', 'PVG', 'JFK', '0935');
insert into Flight values ('China Eastern', 'MU3473', '2022-12-03 18:45:00', '2022-12-03 20:22:00',
    '1021', 'delayed', 'PVG', 'PEK', '0542');
insert into Flight values ('China Eastern', 'MU319', '2022-12-04 10:30:00', '2022-12-04 23:48:00',
    '9857', 'delayed', 'LAX', 'PEK', '0935');
insert into Flight values ('China International Airline', 'CA277', '2021-06-05 14:30:00', '2021-06-06 03:10:00',
    '16352', 'delayed', 'LAX', 'PVG', '4726');
insert into Flight values ('China International Airline', 'CA5473', '2022-12-07 15:25:00', '2022-12-07 17:05:00',
    '654', 'upcoming', 'PEK', 'PVG', '2112');
insert into Flight values ('China International Airline', 'CA388', '2022-12-05 07:05:00', '2022-12-05 19:33:00',
    '23100', 'in-progress', 'PEK', 'JFK', '4726');
insert into Flight values ('Delta Airlines', 'DA522', '2022-12-04 22:35:00', '2022-12-05 09:40:00',
    '9782', 'in-progess', 'BOS', 'PVG', '0567');
insert into Flight values ('Delta Airlines', 'DA144', '2022-12-08 13:15:00', '2022-12-08 14:20:00',
    '453', 'upcoming', 'BOS', 'JFK', '0098'); 
insert into Flight values ('Korean Air', 'KE997', '2022-12-09 14:05:00', '2022-12-09 17:20:00',
    '9930', 'upcoming', 'ICN', 'PEK', '1473');
insert into Flight values ('Korean Air', 'KE054', '2022-12-02 18:30:00', '2022-12-03 06:17:00',
    '29811', 'delayed', 'JFK', 'ICN', '6666');
insert into Flight values ('American Airlines', 'AA876', '2022-12-07 16:07:00', '2022-12-09 21:35:00',
    '1879', 'upcoming', 'LAX', 'BOS', '8712');
insert into Flight values ('American Airlines', 'AA761', '2022-12-05 15:33:00', '2022-12-05 20:02:00',
    '877', 'in-progress', 'BOS', 'LAX', '3333');


insert into Ticket values (1, 'China Eastern', 'MU588', 'tom123@gmail.com', null, '2022-11-30');
insert into Ticket values (2, 'China Eastern', 'MU588', 'Amy456@gmail.com', 'citytrip@163.com', '2022-10-10');
insert into Ticket values (3, 'China Eastern', 'MU3473', 'tom123@gmail.com', null, '2022-09-29');
insert into Ticket values (4, 'China Eastern', 'MU3473', 'Amy456@gmail.com', 'expedia@gmail.com', '2021-12-21');
insert into Ticket values (5, 'China Eastern', 'MU319', 'xiaoming@163.com', 'citytrip@163.com', '2022-05-04');
insert into Ticket values (6, 'Delta Airlines', 'DA144', 'xiaoming@163.com', 'expedia@gmail.com', '2022-05-15');
insert into Ticket values (7, 'China International Airline', 'CA277', 'Amy456@gmail.com', 'Tuniulvxing@qq.com', '2020-03-07');
insert into Ticket values (8, 'Delta Airlines', 'DA144', 'tom123@gmail.com', null, '2022-12-01');
insert into Ticket values (9, 'China Eastern', 'MU319', 'tom123@gmail.com', null, '2022-11-30');
insert into Ticket values (10, 'China International Airline', 'CA277', 'tom123@gmail.com', null, '2020-10-09');
insert into Ticket values (11, 'China International Airline', 'CA277', 'Amy456@gmail.com', 'expedia@gmail.com', '2021-01-03');
insert into Ticket values (12, 'China International Airline', 'CA5473', 'xiaoming@163.com', 'Tuniulvxing@qq.com', '2022-02-04');
insert into Ticket values (13, 'China International Airline', 'CA5473', 'tom123@gmail.com', null, '2021-04-07');
insert into Ticket values (14,'China International Airline', 'CA388', 'xiaoming@163.com', 'expedia@gmail.com', '2022-01-28');
insert into Ticket values (15,'China International Airline', 'CA388', 'Amy456@gmail.com', 'citytrip@163.com', '2022-03-01');
insert into Ticket values (16,'Delta Airlines', 'DA522', 'tom123@gmail.com', null, '2022-04-05');
insert into Ticket values (17,'Delta Airlines', 'DA522', 'Amy456@gmail.com', 'citytrip@163.com', '2021-11-08');
insert into Ticket values (18,'American Airlines', 'AA876', 'shiyuan123@126.com', 'thankyoutrip@163.com', '2021-06-05');
insert into Ticket values (19,'American Airlines', 'AA876', 'andyzhang@126.com', 'citytrip@163.com', '2022-10-03');
insert into Ticket values (20,'American Airlines', 'AA761', 'shiyuan123@126.com', null, '2022-05-02');
insert into Ticket values (21,'American Airlines', 'AA761', 'andyzhang@126.com', null, '2022-05-16');
insert into Ticket values (22,'American Airlines', 'AA761', 'amy456@gmail.com', 'dontknowwhattoadd@qq.com', '2022-03-17');
insert into Ticket values (23,'Korean Air', 'KE054', 'amy456@gmail.com', 'taobao@126.com', '2020-10-18');
insert into Ticket values (24,'Korean Air', 'KE054', 'shiyuan123@126.com', 'dontknowwhattoadd@qq.com', '2021-06-09');
insert into Ticket values (25,'Korean Air', 'KE054', '62836192@qq.com', null, '2022-04-07');
insert into Ticket values (26,'Korean Air', 'KE997', '62836192@qq.com', null, '2022-09-10');
insert into Ticket values (27,'Korean Air', 'KE997', 'xiaoming@163.com', 'taobao@126.com', '2022-01-17');






