// Points-of-sail compass: 8 wedges colored by speed for each heading direction.

const HEADINGS = [0, 45, 90, 135, 180, 225, 270, 315];

const ANGLE_TO_SPEED: Record<number, number> = {
  0: 0,
  45: 1,
  90: 2,
  135: 3,
  180: 2
};

const SPEED_COLORS: Record<number, string> = {
  0: '#4b5563',
  1: '#eab308',
  2: '#22d3ee',
  3: '#22c55e'
};

interface SailCompassProps {
  windDirection: number;
  heading: number;
}

// Convert compass heading (0=N, CW) to SVG (x,y) coordinates.
// In SVG: x increases right, y increases down.
const polarToSVG = (cx: number, cy: number, r: number, compassDeg: number) => ({
  x: cx + r * Math.sin((compassDeg * Math.PI) / 180),
  y: cy - r * Math.cos((compassDeg * Math.PI) / 180)
});

const wedgePath = (cx: number, cy: number, r: number, h: number): string => {
  const p1 = polarToSVG(cx, cy, r, h - 22.5);
  const p2 = polarToSVG(cx, cy, r, h + 22.5);
  return `M ${cx} ${cy} L ${p1.x.toFixed(2)} ${p1.y.toFixed(2)} A ${r} ${r} 0 0 1 ${p2.x.toFixed(2)} ${p2.y.toFixed(2)} Z`;
};

export const SailCompass = ({ windDirection, heading }: SailCompassProps) => {
  const cx = 32;
  const cy = 32;
  const r = 27;
  const labelR = r * 0.62;
  const arrowR = r * 0.82;

  const getSpeed = (h: number): number => {
    const diff = Math.abs(windDirection - h) % 360;
    const angle = Math.min(diff, 360 - diff);
    return ANGLE_TO_SPEED[angle] ?? 0;
  };

  const arrowTip = polarToSVG(cx, cy, arrowR, heading);
  const arrowBase1 = polarToSVG(cx, cy, r * 0.28, heading + 110);
  const arrowBase2 = polarToSVG(cx, cy, r * 0.28, heading - 110);

  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      style={{ display: 'block', flexShrink: 0 }}
    >
      {/* Wedges */}
      {HEADINGS.map((h) => {
        const speed = getSpeed(h);
        return (
          <path
            key={h}
            d={wedgePath(cx, cy, r, h)}
            fill={SPEED_COLORS[speed]}
            stroke="#0f1923"
            strokeWidth="0.8"
          />
        );
      })}

      {/* Speed labels inside each wedge */}
      {HEADINGS.map((h) => {
        const speed = getSpeed(h);
        const lp = polarToSVG(cx, cy, labelR, h);
        return (
          <text
            key={h}
            x={lp.x.toFixed(2)}
            y={lp.y.toFixed(2)}
            textAnchor="middle"
            dominantBaseline="central"
            fontSize="7"
            fontWeight="bold"
            fill={speed === 0 ? '#9ca3af' : '#ffffff'}
          >
            {speed}
          </text>
        );
      })}

      {/* Current heading arrow */}
      <polygon
        points={`${arrowTip.x.toFixed(2)},${arrowTip.y.toFixed(2)} ${arrowBase1.x.toFixed(2)},${arrowBase1.y.toFixed(2)} ${arrowBase2.x.toFixed(2)},${arrowBase2.y.toFixed(2)}`}
        fill="white"
        opacity="0.9"
      />

      {/* Center dot */}
      <circle cx={cx} cy={cy} r="2.5" fill="#0f1923" />
    </svg>
  );
};
