import express from "express";
import authRoutes from "./auth";
import facesRoutes from "./faces";

const router = express.Router();

router.use("/auth", authRoutes);
router.use("/faces", facesRoutes);

export default router;
