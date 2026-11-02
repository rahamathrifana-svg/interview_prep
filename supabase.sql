CREATE TABLE IF NOT EXISTS public.user_progress (
  user_id text PRIMARY KEY,
  email text,
  display_name text,
  photo_url text,
  xp integer NOT NULL DEFAULT 0 CHECK (xp >= 0),
  progress jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can read their own progress" ON public.user_progress;
CREATE POLICY "Users can read their own progress"
ON public.user_progress FOR SELECT
TO authenticated
USING ((select auth.uid())::text = user_id);

DROP POLICY IF EXISTS "Users can insert their own progress" ON public.user_progress;
CREATE POLICY "Users can insert their own progress"
ON public.user_progress FOR INSERT
TO authenticated
WITH CHECK ((select auth.uid())::text = user_id);

DROP POLICY IF EXISTS "Users can update their own progress" ON public.user_progress;
CREATE POLICY "Users can update their own progress"
ON public.user_progress FOR UPDATE
TO authenticated
USING ((select auth.uid())::text = user_id)
WITH CHECK ((select auth.uid())::text = user_id);
