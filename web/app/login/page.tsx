import { redirect } from "next/navigation";
import { LoginForm } from "@/components/login-form";
import { currentUser } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function LoginPage() {
  if (await currentUser()) redirect("/");
  return (
    <div className="login-wrap">
      <section className="card login-card">
        <div className="eyebrow">Personal research workspace</div>
        <h1>Think through papers, not around them.</h1>
        <p className="lead">登录你的 Robotics research cognition system。</p>
        <div style={{ height: 24 }} />
        <LoginForm />
      </section>
    </div>
  );
}
