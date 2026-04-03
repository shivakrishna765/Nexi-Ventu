/**
 * SpaceBackground — CSS-only animated starfield + rotating Saturn-like planet.
 * Pure CSS + SVG, no Three.js needed.
 */

function generateStars(count) {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 2 + 0.5,
    delay: Math.random() * 4,
    duration: Math.random() * 3 + 2,
  }));
}

const STARS = generateStars(160);

export default function SpaceBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      {/* Deep space gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#05040b] via-[#0a0818] to-[#060d1f]" />

      {/* Nebula blobs */}
      <div className="absolute left-[-10%] top-[-5%] h-[500px] w-[500px] rounded-full bg-violet-900/20 blur-[120px]" />
      <div className="absolute right-[-5%] top-[30%] h-[400px] w-[400px] rounded-full bg-cyan-900/15 blur-[100px]" />
      <div className="absolute bottom-[-10%] left-[30%] h-[350px] w-[350px] rounded-full bg-indigo-900/20 blur-[90px]" />

      {/* Starfield */}
      <svg className="absolute inset-0 h-full w-full">
        {STARS.map((s) => (
          <circle
            key={s.id}
            cx={`${s.x}%`}
            cy={`${s.y}%`}
            r={s.size}
            fill="white"
            opacity={0.6}
            style={{ animation: `twinkle ${s.duration}s ${s.delay}s ease-in-out infinite alternate` }}
          />
        ))}
      </svg>

      {/* Saturn-like planet */}
      <div className="absolute right-[8%] top-[12%] h-32 w-32 md:h-48 md:w-48">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-700 via-indigo-800 to-slate-900 shadow-[0_0_60px_rgba(139,92,246,0.4)]" />
        <div
          className="absolute left-[-30%] top-[42%] h-[18%] w-[160%] rounded-full border-2 border-violet-400/40 bg-transparent"
          style={{ transform: "rotateX(70deg)", boxShadow: "0 0 20px rgba(139,92,246,0.3)", animation: "spin-slow 18s linear infinite" }}
        />
        <div className="absolute inset-[-8px] rounded-full bg-violet-500/10 blur-md" />
      </div>

      {/* Floating particles */}
      {[...Array(8)].map((_, i) => (
        <div
          key={i}
          className="absolute h-1 w-1 rounded-full bg-cyan-400/60"
          style={{ left: `${10 + i * 11}%`, top: `${20 + (i % 3) * 25}%`, animation: `float ${3 + i * 0.5}s ${i * 0.3}s ease-in-out infinite alternate` }}
        />
      ))}

      <style>{`
        @keyframes twinkle { from { opacity: 0.2; } to { opacity: 0.9; } }
        @keyframes spin-slow { from { transform: rotateX(70deg) rotateZ(0deg); } to { transform: rotateX(70deg) rotateZ(360deg); } }
        @keyframes float { from { transform: translateY(0px) translateX(0px); } to { transform: translateY(-12px) translateX(6px); } }
      `}</style>
    </div>
  );
}
