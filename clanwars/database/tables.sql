-----------------------------------------------------------
-- In this file there is every CREATE command which was  --
-- used to create all the tables for the bot documented. --
-----------------------------------------------------------

----------------
-- Clan Table --
----------------

CREATE TABLE public.clan (
	name varchar NOT NULL,
	tag varchar NULL,
	owner_id bigint NULL,
	register_time timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),
	role_id int8 NULL,
	gg_amount bigint NOT NULL DEFAULT 0,
	members bigint NOT NULL DEFAULT ARRAY[]::integer[],
	was_member bigint NOT NULL DEFAULT ARRAY[]::integer[],
	approved bool NOT NULL DEFAULT False,
    enabled bool NOT NULL DEFAULT True,
    deleted bool NOT NULL DEFAULT False,
	CONSTRAINT clans_pk PRIMARY KEY (name)
);


------------------
-- Member Table --
------------------

CREATE TABLE public.member (
	member_id int8 NOT NULL,
	ign varchar NULL,
	aliases varchar[] NULL DEFAULT ARRAY[]::varchar[],
	registered_time timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),
	warns int8 NOT NULL DEFAULT 0,
	banned bool NOT NULL DEFAULT False,
	CONSTRAINT member_pk PRIMARY KEY (member_id)
);
