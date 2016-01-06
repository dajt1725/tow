create table tow_enum_donation_type ( value varchar(255) primary key);
insert into tow_enum_donation_type values ('Other'), ('Money'), ('Goods'), ('Services');
alter table tow_donation add donation_type varchar(255) not null default 'Other' references tow_enum_donation_type(value);
alter table tow_donation add donation_notes varchar(255);
