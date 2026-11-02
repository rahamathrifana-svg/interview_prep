# Firebase and Vercel setup

## 1. Configure Firebase

1. Create a Firebase project.
2. Register a web app.
3. In Firebase Authentication, enable Google.
4. Add your deployed Vercel domain under Authentication > Settings > Authorized domains.
5. Copy the Firebase web configuration into the `firebaseConfig` object in [index.html](index.html).
6. No backend environment variables are required.

## 2. Prepare the project

Run locally:

```powershell
cd "E:\interview prep"
python -m http.server 8000
```

Open `http://localhost:8000/index.html`.

Firebase Authentication handles Google sign-in; Supabase stores user profiles and progress.

## 3. Publish with Vercel

1. Create a GitHub repository and push this project folder.
2. Go to Vercel and select **Add New > Project**.
3. Import the GitHub repository.
4. Deploy.
5. Copy the Vercel domain into Firebase Authentication's authorized domains.
6. Redeploy after changing Firebase configuration.

For a Vercel CLI deployment:

```powershell
npx vercel login
npx vercel
npx vercel --prod
```

## 4. Connect Supabase

1. Create a project at supabase.com.
2. In **Authentication > Sign In / Providers > Third-party Auth**, add Firebase as a provider using Firebase project ID `placement-quest-game`.
3. Run [supabase.sql](supabase.sql) in Supabase SQL Editor.
4. Copy the Supabase Project URL and anon key.
5. Set these values in the `supabaseConfig` object in [index.html](index.html):

```javascript
const supabaseConfig={
 url:'https://YOUR-PROJECT.supabase.co',
 anonKey:'YOUR_SUPABASE_ANON_KEY'
};
```

Firebase continues to handle Google sign-in. The Firebase ID token is exchanged with Supabase, and the user's progress is stored in PostgreSQL. Supabase RLS policies allow access only to the matching Firebase UID.
