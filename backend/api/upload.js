import { google } from 'googleapis';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).send('Only POST requests allowed');
  }

  try {
    const { title, author, year, type, license, sourceUrl, fileData, fileName } = req.body;

    const auth = new google.auth.GoogleAuth({
      credentials: {
        type: "service_account",
        project_id: process.env.GOOGLE_PROJECT_ID,
        private_key_id: process.env.GOOGLE_PRIVATE_KEY_ID,
        private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
        client_email: process.env.GOOGLE_CLIENT_EMAIL,
        client_id: process.env.GOOGLE_CLIENT_ID,
      },
      scopes: ['https://www.googleapis.com/auth/drive.file']
    });

    const drive = google.drive({ version: 'v3', auth });
    const buffer = Buffer.from(fileData.split(',')[1], 'base64');

    const file = await drive.files.create({
      requestBody: {
        name: fileName,
        parents: [process.env.DRIVE_FOLDER_ID],
      },
      media: {
        mimeType: 'application/pdf',
        body: Buffer.from(buffer),
      },
      fields: 'id, webViewLink',
    });

    res.status(200).json({ message: 'OK', link: file.data.webViewLink });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: err.message });
  }
}

