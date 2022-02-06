/*
 * MIT License
 *
 * Copyright (c) 2022 GozZzer
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */


CREATE TABLE public.member (
	member_id int8 NOT NULL,
	ign varchar NULL,
	registered_time timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),
	warns int8 NOT NULL DEFAULT 0,
	banned bool NOT NULL DEFAULT False,
	CONSTRAINT member_pk PRIMARY KEY (member_id)
);

CREATE TABLE public.clan (
	name varchar NOT NULL,
	tag varchar NULL,
	owner_id bigint NULL,
	register_time timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),
	role_id int8 NULL,
	gg_amount bigint NOT NULL DEFAULT 0,
	members _int8 NOT NULL DEFAULT ARRAY[]::integer[],
	was_member _int8 NOT NULL DEFAULT ARRAY[]::integer[],
	approved bool NOT NULL DEFAULT False,
    enabled bool NOT NULL DEFAULT True,
    deleted bool NOT NULL DEFAULT False,
	CONSTRAINT clans_pk PRIMARY KEY (name)
);
