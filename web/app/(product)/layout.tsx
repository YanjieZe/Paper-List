import { Navigation } from "@/components/navigation";
import { requireUser } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function ProductLayout({ children }: { children: React.ReactNode }) {
  const user = await requireUser();
  return (
    <div className="shell">
      <Navigation username={user.username} />
      <main className="main">{children}</main>
    </div>
  );
}
