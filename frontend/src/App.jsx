import { Route, Routes, useLocation, Navigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useAuth } from "./context/AuthContext";
import { roleToRoute } from "./utils/session";
import SpaceBackground from "./components/SpaceBackground";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Home              from "./pages/Home";
import Login             from "./pages/Login";
import InvestorDashboard from "./pages/InvestorDashboard";
import FounderDashboard  from "./pages/FounderDashboard";
import TeamDashboard     from "./pages/TeamDashboard";
import CollaboratorDashboard from "./pages/CollaboratorDashboard";
import Startups          from "./pages/Startups";
import Profile           from "./pages/Profile";
import Admin             from "./pages/Admin";

function Fade({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.22 }}
    >
      {children}
    </motion.div>
  );
}

export default function App() {
  const location = useLocation();
  const { user } = useAuth();

  return (
    <div className="relative min-h-screen text-white">
      <SpaceBackground />
      <div className="relative z-10 flex min-h-screen flex-col">
        <Navbar />
        <main className="flex-1">
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              {/* Public */}
              <Route path="/" element={<Fade><Home /></Fade>} />
              <Route
                path="/login"
                element={
                  user
                    ? <Navigate to={roleToRoute(user.role)} replace />
                    : <Fade><Login /></Fade>
                }
              />

              {/* Role-protected dashboards */}
              <Route
                path="/investor-dashboard"
                element={
                  <ProtectedRoute allowedRoles={["investor"]}>
                    <Fade><InvestorDashboard /></Fade>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/founder-dashboard"
                element={
                  <ProtectedRoute allowedRoles={["founder"]}>
                    <Fade><FounderDashboard /></Fade>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/team-dashboard"
                element={
                  <ProtectedRoute allowedRoles={["seeker", "member"]}>
                    <Fade><TeamDashboard /></Fade>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/collaborator-dashboard"
                element={
                  <ProtectedRoute allowedRoles={["collaborator"]}>
                    <Fade><CollaboratorDashboard /></Fade>
                  </ProtectedRoute>
                }
              />

              {/* Auth-required but any role */}
              <Route
                path="/startups"
                element={
                  <ProtectedRoute>
                    <Fade><Startups /></Fade>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Fade><Profile /></Fade>
                  </ProtectedRoute>
                }
              />

              {/* Admin — backend also enforces is_admin */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute adminOnly>
                    <Fade><Admin /></Fade>
                  </ProtectedRoute>
                }
              />

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </main>
        <Footer />
      </div>
    </div>
  );
}

