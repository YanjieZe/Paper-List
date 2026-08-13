import { LogoutButton } from "@/components/logout-button";
import { ProfileForm } from "@/components/profile-form";
import { requireUser } from "@/lib/auth";
import { db } from "@/lib/db";

export default async function SettingsPage(){const user=await requireUser();const [profiles,settings]=await Promise.all([db()`select markdown,version,updated_at from research_profiles where user_id=${user.id}`,db()`select key,value from app_settings order by key`]);return <div className="page"><header className="page-head"><div><div className="eyebrow">Configuration</div><h1>Settings</h1><p className="lead">模型角色、费用护栏和你的研究画像彼此独立，升级模型不需要改 agent 代码。</p></div><LogoutButton/></header><ProfileForm initial={profiles[0]?.markdown??""}/><section className="section grid grid-2">{settings.map((setting)=><article className="card card-pad" key={setting.key}><h2>{setting.key}</h2><pre style={{whiteSpace:"pre-wrap",fontSize:12}}>{JSON.stringify(setting.value,null,2)}</pre></article>)}</section></div>}
