# Firebase, SQLite, and Vercel setup

## 1. Configure Firebase

1. Create a Firebase project.
2. Register a web app.
3. In Firebase Authentication, enable Google.
4. Add your deployed Vercel domain under Authentication > Settings > Authorized domains.
5. Copy the Firebase web configuration into the `firebaseConfig` object in [index.html](index.html).
6. In Vercel, add this environment variable:

   ```text
   FIREBASE_PROJECT_ID=your-firebase-project-id
   ```

## 2. Prepare the project

Run locally:

```powershell
cd "E:\interview prep"
.\start-backend.cmd
```

Open `http://localhost:8000/index.html`.

SQLite is initialized from [database.sql](database.sql) automatically.

## 3. Publish with Vercel

1. Create a GitHub repository and push this project folder.
2. Go to Vercel and select **Add New > Project**.
3. Import the GitHub repository.
4. Add `FIREBASE_PROJECT_ID` in Project Settings > Environment Variables.
5. Deploy.
6. Copy the Vercel domain into Firebase Authentication's authorized domains.
7. Redeploy after changing Firebase configuration.

For a Vercel CLI deployment:

```powershell
npx vercel login
npx vercel
npx vercel --prod
```

## 4. SQLite production limitation

Vercel serverless functions are temporary. The `/tmp/placement_quest.db` database may be lost between deployments, cold starts, or instances.

For persistent production data, use one of:

- Firebase Firestore
- Vercel Postgres or another hosted PostgreSQL database
- Turso
- PlanetScale MySQL

Keep Firebase Authentication for Google sign-in, then store application progress in the hosted database using the verified Firebase UID.
