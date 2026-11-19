import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import "@fontsource-variable/vazirmatn";
import "./styles.css";
import { queryClient } from "./lib/api";
import { Router } from "./app/router";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Router />
      <Toaster position="bottom-left" dir="rtl" richColors />
    </QueryClientProvider>
  </StrictMode>,
);
