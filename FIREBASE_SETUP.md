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

Firebase Authentication handles Google sign-in. Learning progress is saved locally in this browser and is not synced across devices.

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

