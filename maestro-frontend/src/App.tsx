import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        {/* Pokud bys chtěla přidat další stránky, přidáš je sem */}
      </Routes>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;