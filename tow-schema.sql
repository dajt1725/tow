SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE IF NOT EXISTS `tow_event` (
  `event_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(128) CHARACTER SET utf8 NOT NULL,
  `type` enum('Unknown','Mystery School','Ritual','Workshop') NOT NULL,
  `starts_on` date NOT NULL,
  `ends_on` date NOT NULL,
  `base_cost` int(11) NOT NULL,
  `ceus` int(11) DEFAULT NULL,
  `event_notes` text,
  PRIMARY KEY (`event_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

insert into tow_event (name, type, starts_on, ends_on, base_cost, event_notes)
 values ('Dummy Event','Unknown', '2000-01-01', '2000-01-01', 0, 'Remove this event once you have added a real event.');

CREATE TABLE IF NOT EXISTS `tow_person` (
  `person_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` text NOT NULL,
  `last_name` text,
  `craft_name` text,
  `membership_status` enum('Unknown','Other','Nonmember','General','Honored','Ministerial') NOT NULL DEFAULT 'Unknown',
  `member_since` date DEFAULT NULL,
  `street_address_1` text,
  `street_address_2` text,
  `town_village_city` text,
  `province_state` text,
  `postal_code` text,
  `country` text,
  `date_of_birth` date DEFAULT NULL,
  `gender` enum('Unknown','Male','Female','Other') NOT NULL DEFAULT 'Unknown',
  `is_ordained` tinyint(4) NOT NULL DEFAULT '0',
  `ordination_date` date DEFAULT NULL,
  `ordination_renewal_date` date DEFAULT NULL,
  `person_notes` text,
  `volunteer_status` enum('Unknown','No','Former','Active') NOT NULL DEFAULT 'Unknown',
  `ministries` set('Aquarius','Aries','Cancer','Capricorn','Gemini','Leo','Libra','Pisces','Sagittarius','Scorpio','Taurus','Virgo') NOT NULL DEFAULT '',
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

insert into tow_person (first_name, person_notes)
 values ('Dummy Person','Remove this person once you have added a real person.');

CREATE TABLE IF NOT EXISTS `tow_contact` (
  `person_id` int(10) unsigned NOT NULL,
  `type` enum('Unknown','email','email/home','email/work','phone','phone/home','phone/work','phone/cell','other') NOT NULL,
  `address` varchar(128) NOT NULL,
  `contact_notes` text,
  PRIMARY KEY (`person_id`,`type`,`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `tow_contact`
  ADD CONSTRAINT `tow_contact_ibfk_1` FOREIGN KEY (`person_id`) REFERENCES `tow_person` (`person_id`);

CREATE TABLE IF NOT EXISTS `tow_enum_donation_type` (
  `value` varchar(64) NOT NULL,
  PRIMARY KEY (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `tow_enum_donation_type` (`value`) VALUES
('Goods'),
('Money'),
('Other'),
('Services');

CREATE TABLE IF NOT EXISTS `tow_donation` (
  `donation_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `person_id` int(10) unsigned NOT NULL,
  `donation_date` date NOT NULL,
  `donation_amount` int(10) unsigned NOT NULL,
  `donation_status` enum('Unknown','Pledged','Cancelled','Complete') NOT NULL,
  `donation_type` varchar(64) NOT NULL DEFAULT 'Other',
  `donation_notes` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`donation_id`),
  KEY `person_id` (`person_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

ALTER TABLE `tow_donation`
  ADD CONSTRAINT `tow_donation_ibfk_1` FOREIGN KEY (`person_id`) REFERENCES `tow_person` (`person_id`),
  ADD CONSTRAINT `tow_donation_ibfk_2` FOREIGN KEY (`donation_type`) REFERENCES `tow_enum_donation_type` (`value`);

CREATE TABLE IF NOT EXISTS `tow_person_event` (
  `person_id` int(10) unsigned NOT NULL,
  `event_id` int(10) unsigned NOT NULL,
  `type` enum('Unknown','Teacher','Volunteer','Student','Auditor','Other') NOT NULL,
  `status` enum('Unknown','Signed-Up','Cancelled','In-Progress','Completed') NOT NULL,
  `payment_status` enum('Unknown','Paid','Not Paid','Scholarship','Donation Package','ISBE') NOT NULL,
  `enrolled` date DEFAULT NULL,
  PRIMARY KEY (`person_id`,`event_id`),
  KEY `event_id` (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `tow_person_event`
  ADD CONSTRAINT `tow_person_event_ibfk_1` FOREIGN KEY (`person_id`) REFERENCES `tow_person` (`person_id`),
  ADD CONSTRAINT `tow_person_event_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `tow_event` (`event_id`);

CREATE TABLE IF NOT EXISTS `tow_user` (
  `user` varchar(16) NOT NULL,
  `salt` int(10) unsigned NOT NULL,
  `b64_passwd` char(44) NOT NULL default '********************************************',
  `permissions` set('debug','donation','event','person','user') CHARACTER SET utf8 NOT NULL DEFAULT '',
  `user_notes` text,
  `expiration` int(10) unsigned NOT NULL DEFAULT '3600',
  PRIMARY KEY (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into tow_user (user, salt, password, permissions, user_notes) values ('hack',8675309,x'd78928f88c9b5bf549e001ef69c2aab04b61df9afd1fbbaf631dff61b0a3b1f0', 'debug,donation,event,person,user', 'Remove this user entry once you have added a real user.');

CREATE TABLE IF NOT EXISTS `tow_session` (
  `user` varchar(16) NOT NULL,
  `id` int(10) unsigned NOT NULL,
  `host` text,
  `expires` datetime NOT NULL,
  `permissions` set('debug','donation','event','person','user') CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `tow_session`
  ADD CONSTRAINT `tow_session_ibfk_1` FOREIGN KEY (`user`) REFERENCES `tow_user` (`user`);


