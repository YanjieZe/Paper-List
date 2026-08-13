"use client";
import { useRouter } from "next/navigation";
export function LogoutButton(){const router=useRouter();async function logout(){await fetch("/api/auth/logout",{method:"POST"});router.push("/login");router.refresh()}return <button className="button secondary" onClick={logout}>Sign out</button>}
