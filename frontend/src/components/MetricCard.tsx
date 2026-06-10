import { ReactNode } from "react";

type Props = {
  label: string;
  value: string;
  helper: string;
  icon: ReactNode;
};

export function MetricCard({ label, value, helper, icon }: Props) {
  return (
    <section className="metric-card">
      <div className="metric-icon">{icon}</div>
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{helper}</span>
    </section>
  );
}
