
  create table "public"."collection_games" (
    "id" uuid not null default extensions.uuid_generate_v4(),
    "collection_id" uuid not null,
    "game_id" uuid not null,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."collection_games" enable row level security;


  create table "public"."collection_media" (
    "id" uuid not null default extensions.uuid_generate_v4(),
    "collection_id" uuid not null,
    "library_item_id" uuid not null,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."collection_media" enable row level security;


  create table "public"."collections" (
    "id" uuid not null default extensions.uuid_generate_v4(),
    "user_id" uuid not null,
    "name" text not null,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."collections" enable row level security;


  create table "public"."games" (
    "id" uuid not null default extensions.uuid_generate_v4(),
    "user_id" uuid not null,
    "rawg_id" integer not null,
    "title" text not null,
    "background_image" text,
    "status" text default 'unplayed'::text,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."games" enable row level security;


  create table "public"."user_library" (
    "id" uuid not null default extensions.uuid_generate_v4(),
    "user_id" uuid not null,
    "tmdb_id" integer not null,
    "media_type" text not null,
    "title" text not null,
    "poster_path" text,
    "watched" text default 'not_watched'::text,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."user_library" enable row level security;

CREATE UNIQUE INDEX collection_games_collection_id_game_id_key ON public.collection_games USING btree (collection_id, game_id);

CREATE UNIQUE INDEX collection_games_pkey ON public.collection_games USING btree (id);

CREATE UNIQUE INDEX collection_media_collection_id_library_item_id_key ON public.collection_media USING btree (collection_id, library_item_id);

CREATE UNIQUE INDEX collection_media_pkey ON public.collection_media USING btree (id);

CREATE UNIQUE INDEX collections_pkey ON public.collections USING btree (id);

CREATE UNIQUE INDEX games_pkey ON public.games USING btree (id);

CREATE UNIQUE INDEX unique_user_game ON public.games USING btree (user_id, rawg_id);

CREATE UNIQUE INDEX unique_user_media ON public.user_library USING btree (user_id, tmdb_id);

CREATE UNIQUE INDEX user_library_pkey ON public.user_library USING btree (id);

alter table "public"."collection_games" add constraint "collection_games_pkey" PRIMARY KEY using index "collection_games_pkey";

alter table "public"."collection_media" add constraint "collection_media_pkey" PRIMARY KEY using index "collection_media_pkey";

alter table "public"."collections" add constraint "collections_pkey" PRIMARY KEY using index "collections_pkey";

alter table "public"."games" add constraint "games_pkey" PRIMARY KEY using index "games_pkey";

alter table "public"."user_library" add constraint "user_library_pkey" PRIMARY KEY using index "user_library_pkey";

alter table "public"."collection_games" add constraint "collection_games_collection_id_fkey" FOREIGN KEY (collection_id) REFERENCES public.collections(id) ON DELETE CASCADE not valid;

alter table "public"."collection_games" validate constraint "collection_games_collection_id_fkey";

alter table "public"."collection_games" add constraint "collection_games_collection_id_game_id_key" UNIQUE using index "collection_games_collection_id_game_id_key";

alter table "public"."collection_games" add constraint "collection_games_game_id_fkey" FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE not valid;

alter table "public"."collection_games" validate constraint "collection_games_game_id_fkey";

alter table "public"."collection_media" add constraint "collection_media_collection_id_fkey" FOREIGN KEY (collection_id) REFERENCES public.collections(id) ON DELETE CASCADE not valid;

alter table "public"."collection_media" validate constraint "collection_media_collection_id_fkey";

alter table "public"."collection_media" add constraint "collection_media_collection_id_library_item_id_key" UNIQUE using index "collection_media_collection_id_library_item_id_key";

alter table "public"."collection_media" add constraint "collection_media_library_item_id_fkey" FOREIGN KEY (library_item_id) REFERENCES public.user_library(id) ON DELETE CASCADE not valid;

alter table "public"."collection_media" validate constraint "collection_media_library_item_id_fkey";

alter table "public"."games" add constraint "unique_user_game" UNIQUE using index "unique_user_game";

alter table "public"."user_library" add constraint "unique_user_media" UNIQUE using index "unique_user_media";

grant delete on table "public"."collection_games" to "anon";

grant insert on table "public"."collection_games" to "anon";

grant references on table "public"."collection_games" to "anon";

grant select on table "public"."collection_games" to "anon";

grant trigger on table "public"."collection_games" to "anon";

grant truncate on table "public"."collection_games" to "anon";

grant update on table "public"."collection_games" to "anon";

grant delete on table "public"."collection_games" to "authenticated";

grant insert on table "public"."collection_games" to "authenticated";

grant references on table "public"."collection_games" to "authenticated";

grant select on table "public"."collection_games" to "authenticated";

grant trigger on table "public"."collection_games" to "authenticated";

grant truncate on table "public"."collection_games" to "authenticated";

grant update on table "public"."collection_games" to "authenticated";

grant delete on table "public"."collection_games" to "service_role";

grant insert on table "public"."collection_games" to "service_role";

grant references on table "public"."collection_games" to "service_role";

grant select on table "public"."collection_games" to "service_role";

grant trigger on table "public"."collection_games" to "service_role";

grant truncate on table "public"."collection_games" to "service_role";

grant update on table "public"."collection_games" to "service_role";

grant delete on table "public"."collection_media" to "anon";

grant insert on table "public"."collection_media" to "anon";

grant references on table "public"."collection_media" to "anon";

grant select on table "public"."collection_media" to "anon";

grant trigger on table "public"."collection_media" to "anon";

grant truncate on table "public"."collection_media" to "anon";

grant update on table "public"."collection_media" to "anon";

grant delete on table "public"."collection_media" to "authenticated";

grant insert on table "public"."collection_media" to "authenticated";

grant references on table "public"."collection_media" to "authenticated";

grant select on table "public"."collection_media" to "authenticated";

grant trigger on table "public"."collection_media" to "authenticated";

grant truncate on table "public"."collection_media" to "authenticated";

grant update on table "public"."collection_media" to "authenticated";

grant delete on table "public"."collection_media" to "service_role";

grant insert on table "public"."collection_media" to "service_role";

grant references on table "public"."collection_media" to "service_role";

grant select on table "public"."collection_media" to "service_role";

grant trigger on table "public"."collection_media" to "service_role";

grant truncate on table "public"."collection_media" to "service_role";

grant update on table "public"."collection_media" to "service_role";

grant delete on table "public"."collections" to "anon";

grant insert on table "public"."collections" to "anon";

grant references on table "public"."collections" to "anon";

grant select on table "public"."collections" to "anon";

grant trigger on table "public"."collections" to "anon";

grant truncate on table "public"."collections" to "anon";

grant update on table "public"."collections" to "anon";

grant delete on table "public"."collections" to "authenticated";

grant insert on table "public"."collections" to "authenticated";

grant references on table "public"."collections" to "authenticated";

grant select on table "public"."collections" to "authenticated";

grant trigger on table "public"."collections" to "authenticated";

grant truncate on table "public"."collections" to "authenticated";

grant update on table "public"."collections" to "authenticated";

grant delete on table "public"."collections" to "service_role";

grant insert on table "public"."collections" to "service_role";

grant references on table "public"."collections" to "service_role";

grant select on table "public"."collections" to "service_role";

grant trigger on table "public"."collections" to "service_role";

grant truncate on table "public"."collections" to "service_role";

grant update on table "public"."collections" to "service_role";

grant delete on table "public"."games" to "anon";

grant insert on table "public"."games" to "anon";

grant references on table "public"."games" to "anon";

grant select on table "public"."games" to "anon";

grant trigger on table "public"."games" to "anon";

grant truncate on table "public"."games" to "anon";

grant update on table "public"."games" to "anon";

grant delete on table "public"."games" to "authenticated";

grant insert on table "public"."games" to "authenticated";

grant references on table "public"."games" to "authenticated";

grant select on table "public"."games" to "authenticated";

grant trigger on table "public"."games" to "authenticated";

grant truncate on table "public"."games" to "authenticated";

grant update on table "public"."games" to "authenticated";

grant delete on table "public"."games" to "service_role";

grant insert on table "public"."games" to "service_role";

grant references on table "public"."games" to "service_role";

grant select on table "public"."games" to "service_role";

grant trigger on table "public"."games" to "service_role";

grant truncate on table "public"."games" to "service_role";

grant update on table "public"."games" to "service_role";

grant delete on table "public"."user_library" to "anon";

grant insert on table "public"."user_library" to "anon";

grant references on table "public"."user_library" to "anon";

grant select on table "public"."user_library" to "anon";

grant trigger on table "public"."user_library" to "anon";

grant truncate on table "public"."user_library" to "anon";

grant update on table "public"."user_library" to "anon";

grant delete on table "public"."user_library" to "authenticated";

grant insert on table "public"."user_library" to "authenticated";

grant references on table "public"."user_library" to "authenticated";

grant select on table "public"."user_library" to "authenticated";

grant trigger on table "public"."user_library" to "authenticated";

grant truncate on table "public"."user_library" to "authenticated";

grant update on table "public"."user_library" to "authenticated";

grant delete on table "public"."user_library" to "service_role";

grant insert on table "public"."user_library" to "service_role";

grant references on table "public"."user_library" to "service_role";

grant select on table "public"."user_library" to "service_role";

grant trigger on table "public"."user_library" to "service_role";

grant truncate on table "public"."user_library" to "service_role";

grant update on table "public"."user_library" to "service_role";


  create policy "Dono da coleção gerencia os jogos dela"
  on "public"."collection_games"
  as permissive
  for all
  to authenticated
using ((EXISTS ( SELECT 1
   FROM public.collections
  WHERE ((collections.id = collection_games.collection_id) AND (collections.user_id = auth.uid())))));



  create policy "Dono da coleção gerencia as mídias dela"
  on "public"."collection_media"
  as permissive
  for all
  to authenticated
using ((EXISTS ( SELECT 1
   FROM public.collections
  WHERE ((collections.id = collection_media.collection_id) AND (collections.user_id = auth.uid())))));



  create policy "Dono gerencia suas coleções"
  on "public"."collections"
  as permissive
  for all
  to authenticated
using ((auth.uid() = user_id))
with check ((auth.uid() = user_id));



  create policy "Dono gerencia seus games"
  on "public"."games"
  as permissive
  for all
  to authenticated
using ((auth.uid() = user_id))
with check ((auth.uid() = user_id));



  create policy "Dono gerencia sua biblioteca"
  on "public"."user_library"
  as permissive
  for all
  to authenticated
using ((auth.uid() = user_id))
with check ((auth.uid() = user_id));



