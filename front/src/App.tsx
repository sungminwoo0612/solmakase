import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Home } from './pages/Home';
import { Requirements } from './pages/Requirements';
import { Analysis } from './pages/Analysis';
import { Infrastructure } from './pages/Infrastructure';
import { Deployment } from './pages/Deployment';
import { Downloads } from './pages/Downloads';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/requirements" element={<Requirements />} />
            <Route path="/analysis/:requirementId" element={<Analysis />} />
            <Route path="/design/:requirementId" element={<Infrastructure />} />
            <Route path="/infrastructure/:infrastructureId/iac" element={<Infrastructure />} />
            <Route path="/deployment/:infrastructureId" element={<Deployment />} />
            <Route path="/downloads/:infrastructureId" element={<Downloads />} />
            <Route path="*" element={<div className="p-8 text-center">404 - 페이지를 찾을 수 없습니다</div>} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
