import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Canonical route for each role — single source of truth
const ROLE_ROUTES = {
  investor:     "/investor-dashboard",
  founder:      "/founder-dashboard",
  seeker:       "/team-dashboard",
  member:       "/team-dashboard",   // legacy alias
  collaborator: "/collaborator-dashboard",
};

function normaliseRole(role) {
  const r = (role || "").toLowerCase().trim();
  return r === "member" ? "seeker" : r;
}

/**
 * ProtectedRoute
 *
 * Props:
 *   allowedRoles  — string[] of roles allowed (omit = any authenticated user)
 *   adminOnly     — boolean, only is_admin users
 */
export default function ProtectedRoute({ children, allowedRoles, adminOnly = false }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Still validating token — show spinner, don't redirect yet
  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-violet-500 border-t-transparent" />
      </div>
    );
  }

  // Not authenticated → go to login, remember where they were
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Admin gate
  if (adminOnly && !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  // Role gate
  if (allowedRoles && allowedRoles.length > 0) {
    const effective = normaliseRole(user.role);
    if (!allowedRoles.map(normaliseRole).includes(effective)) {
      // Send them to their own dashboard instead of a 403
      const ownRoute = ROLE_ROUTES[effective] || ROLE_ROUTES[user.role] || "/team-dashboard";
      return <Navigate to={ownRoute} replace />;
    }
  }

  return children;
}
