import express from "express";
import multer from "multer";
import fs from "fs";
import path from "path";

const router = express.Router();

const facesDir = path.join(process.cwd(), "faces");
if (!fs.existsSync(facesDir)) {
  fs.mkdirSync(facesDir, { recursive: true });
  console.log("📁 Carpeta 'faces' creada.");
}

const storage = multer.diskStorage({
  destination: (_, __, cb) => cb(null, facesDir),
  filename: (req, file, cb) => {
    const username = (req.body.username || "unknown").toLowerCase();
    cb(null, `${username}.npy`);
  },
});
const upload = multer({ storage });

router.post("/upload", upload.single("face_file"), (req, res) => {
  try {
    if (!req.body.username || !req.file)
      return res.status(400).json({ ok: false, error: "Faltan datos" });

    console.log(` Rostro recibido: ${req.file.filename}`);
    res.json({ ok: true, filename: req.file.filename });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: "Error interno" });
  }
});

router.get("/download/:username", (req, res) => {
  const filePath = path.join(facesDir, `${req.params.username}.npy`);
  if (!fs.existsSync(filePath))
    return res.status(404).json({ ok: false, error: "Archivo no encontrado" });
  res.download(filePath);
});

export default router;
