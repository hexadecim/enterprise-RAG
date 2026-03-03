"use client";

import { Box, Button, Chip, Container, Stack, Typography } from "@mui/material";
import { BrainCircuit, Database, Server, Shield } from "lucide-react";

const features = [
  {
    icon: <BrainCircuit size={32} />,
    title: "Semantic Search",
    description: "Vector-powered retrieval via Qdrant for high-precision context lookup.",
  },
  {
    icon: <Database size={32} />,
    title: "Knowledge Ingestion",
    description: "Upload, chunk, and embed documents into your private knowledge base.",
  },
  {
    icon: <Server size={32} />,
    title: "FastAPI Backend",
    description: "Async Python API handling embeddings, chat, and document management.",
  },
  {
    icon: <Shield size={32} />,
    title: "Secure by Default",
    description: "OIDC / NextAuth integration ensures only authenticated users query the RAG.",
  },
];

export default function HomePage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        px: 2,
      }}
    >
      <Container maxWidth="md">
        {/* Badge */}
        <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
          <Chip
            label="Enterprise RAG Platform · v0.1"
            sx={{
              bgcolor: "rgba(255,255,255,0.1)",
              color: "white",
              backdropFilter: "blur(8px)",
              border: "1px solid rgba(255,255,255,0.2)",
              fontWeight: 600,
            }}
          />
        </Box>

        {/* Headline */}
        <Typography
          variant="h2"
          fontWeight={800}
          textAlign="center"
          sx={{ lineHeight: 1.15, mb: 2 }}
        >
          Enterprise-Grade
          <br />
          <Box
            component="span"
            sx={{
              background: "linear-gradient(90deg, #a78bfa, #60a5fa)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Retrieval-Augmented Generation
          </Box>
        </Typography>

        <Typography
          variant="h6"
          textAlign="center"
          sx={{ color: "rgba(255,255,255,0.65)", mb: 5, fontWeight: 400 }}
        >
          Secure, scalable, and self-hosted AI knowledge platform built on Next.js&nbsp;15,
          FastAPI&nbsp;and&nbsp;Qdrant.
        </Typography>

        {/* CTAs */}
        <Stack direction="row" spacing={2} justifyContent="center" mb={8}>
          <Button
            variant="contained"
            size="large"
            href="/api/auth/signin"
            sx={{
              background: "linear-gradient(90deg, #7c3aed, #2563eb)",
              borderRadius: 99,
              px: 4,
              py: 1.5,
              fontWeight: 700,
              textTransform: "none",
              "&:hover": { opacity: 0.9 },
            }}
          >
            Get Started
          </Button>
          <Button
            variant="outlined"
            size="large"
            href="http://localhost:8000/docs"
            target="_blank"
            sx={{
              borderRadius: 99,
              px: 4,
              py: 1.5,
              fontWeight: 700,
              textTransform: "none",
              color: "white",
              borderColor: "rgba(255,255,255,0.3)",
              "&:hover": { borderColor: "white", bgcolor: "rgba(255,255,255,0.06)" },
            }}
          >
            API Docs
          </Button>
        </Stack>

        {/* Feature cards */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
            gap: 3,
          }}
        >
          {features.map((f) => (
            <Box
              key={f.title}
              sx={{
                p: 3,
                borderRadius: 3,
                background: "rgba(255,255,255,0.05)",
                backdropFilter: "blur(12px)",
                border: "1px solid rgba(255,255,255,0.12)",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: "0 12px 40px rgba(0,0,0,0.4)",
                },
              }}
            >
              <Box sx={{ color: "#a78bfa", mb: 1.5 }}>{f.icon}</Box>
              <Typography variant="h6" fontWeight={700} mb={0.5}>
                {f.title}
              </Typography>
              <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.6)" }}>
                {f.description}
              </Typography>
            </Box>
          ))}
        </Box>
      </Container>
    </Box>
  );
}
