export function PageHeader({ icon, title, subtitle }: { icon: React.ReactNode, title: string, subtitle: string }) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-heading font-bold flex items-center gap-3">
        <span>{icon}</span> {title}
      </h1>
      <p className="text-text-m mt-2">{subtitle}</p>
    </div>
  );
}
