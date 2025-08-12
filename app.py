// src/App.jsx
import React, { useEffect, useState, createContext } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Header from './components/Header';
import Hero from './components/Hero';
import About from './components/About';
import Services from './components/Services';
import BlogSection from './components/BlogSection';
import Reviews from './components/Reviews';
import Contact from './components/Contact';
import LocationSection from './components/LocationSection';
import Footer from './components/Footer';
import WhatsAppWidget from './components/WhatsAppWidget';
import ScrollToTop from './components/ScrollToTop';
import AdminApp from './pages/admin/AdminApp';
import BlogPost from './pages/BlogPost';
import ThemeProvider from './components/ThemeProvider';

import { api } from './lib/api';

// Contexto leve para disponibilizar configurações do backend (opcional de usar)
export const SettingsContext = createContext({ settings: {}, setSettings: () => {} });

function App() {
  const [settings, setSettings] = useState({});
  const [loadingSettings, setLoadingSettings] = useState(true);
  const [settingsError, setSettingsError] = useState(null);

  useEffect(() => {
    let abort = false;

    async function loadSettings() {
      try {
        setLoadingSettings(true);
        setSettingsError(null);

        // Busca as configurações no backend
        // GET <VITE_API_BASE_URL>/settings   (já apontamos VITE_API_BASE_URL para a raiz do backend)
        const data = await api('/settings');

        if (!abort) {
          setSettings(data || {});
          // Se houver SEO nas configs, ajusta o título da página
          const title =
            data?.seo?.title ||
            data?.site_info?.title ||
            'Dr. Rodrigo Sguario - Cardiologista';
          if (title) document.title = title;
        }
      } catch (err) {
        if (!abort) {
          console.error('Falha ao carregar configurações:', err);
          setSettingsError(err.message || 'Erro ao carregar configurações');
        }
      } finally {
        if (!abort) setLoadingSettings(false);
      }
    }

    loadSettings();
    return () => {
      abort = true;
    };
  }, []);

  // Você pode exibir um skeleton leve durante o primeiro load, se quiser
  // Aqui apenas seguimos renderizando normalmente — os componentes podem ler do contexto quando precisarem.

  return (
    <ThemeProvider>
      <SettingsContext.Provider value={{ settings, setSettings, loadingSettings, settingsError }}>
        <Router>
          <div className="min-h-screen bg-background text-foreground">
            <Routes>
              <Route path="/admin/*" element={<AdminApp />} />
              <Route path="/blog/:slug" element={<BlogPost />} />
              <Route
                path="/"
                element={
                  <>
                    <Header />
                    <main>
                      <Hero />
                      <About />
                      <Services />
                      <BlogSection />
                      <Reviews />
                      <Contact />
                      <LocationSection />
                    </main>
                    <Footer />
                    <WhatsAppWidget />
                    <ScrollToTop />
                  </>
                }
              />
            </Routes>
          </div>
        </Router>
      </SettingsContext.Provider>
    </ThemeProvider>
  );
}

export default App;