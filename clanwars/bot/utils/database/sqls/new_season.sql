CREATE SEQUENCE public.game_id
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;


CREATE TABLE public.games (
	game_id int8 NOT NULL DEFAULT nextval('game_id'::regclass),
	message_id int8 NULL,
	text_channel_id int8 NULL,
	voice_channel_1 int8 NULL,
	voice_channel_2 int8 NULL,
	clan_1 varchar NULL,
	clan_2 varchar NULL,
	clan_1_members _int8 NULL,
	clan_2_members _int8 NULL,
	winner varchar NULL,
	submitted bool NULL DEFAULT false,
	scored bool NULL DEFAULT false,
	"left" _int8 NULL,
	proof bytea NULL,
	map varchar NULL,
	CONSTRAINT games_pkey PRIMARY KEY (game_id)
);


