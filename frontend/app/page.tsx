"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import FileInfo from "./file";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export default function SimpleAPIUI() {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [files, setFiles] = useState([]);
  const [uploadFile, setUploadFile] = useState(Object);
  const [userId, setUserId] = useState(0);

  const api = async (path: string, options: any = {}) => {
    const res = await fetch(new URL(BASE_URL + path), {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    return res.json();
  };

  const login = async () => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    const data = await api("/api/token", {
      method: "POST",
      body: form,
    });
    setToken(data.access_token);
    const res = await fetch(new URL(BASE_URL + "/api/user/me"), {
      headers: {
        ...({Authorization: `Bearer ${data.access_token}`})
      },
    });
    const userData = await res.json();
    setUserId(userData["id"]);
   };

  const register = async () => {
    await api(`/api/register?username=${username}&password=${password}&email=${email}`, {
      method: "POST",
    });
  };

  const listFiles = async () => {
    const data = await api("/api/list_files");
    setFiles(data["files"] || []);
  };

  const upload = async () => {
    const form = new FormData();
    form.append("file", uploadFile);
    await api("/api/upload", { method: "POST", body: form });
    listFiles();
  };

  useEffect(() => {
    if (token) listFiles();
  }, [token]);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <Card>
        <CardContent className="space-y-3 p-4">
          <h2 className="text-xl font-bold">Auth</h2>

          <input
            className="border p-2 w-full"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            className="border p-2 w-full"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            className="border p-2 w-full"
            placeholder="Email (for register)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <div className="flex gap-2">
            <Button onClick={login}>Login</Button>
            <Button onClick={register} variant="secondary">Register</Button>
          </div>
        </CardContent>
      </Card>

      {token && (
        <Card>
          <CardContent className="space-y-4 p-4">
            <h2 className="text-xl font-bold">Files</h2>
            <div className="flex items-center gap-2">
              <input
                type="file"
                onChange={(e) => {
                  if (e != null && e.target != null && e.target.files != null)
                    setUploadFile(e.target.files[0]);
                }}
                className="border p-2"
              />
              <Button onClick={upload}>Upload</Button>
            </div>

            <ul className="space-y-2">
              {files.map((f, i) => (
                <li key={i} className="border p-2 rounded-xl flex justify-between">
                  <FileInfo file={JSON.stringify(f)} api={api} i={i} setFiles={setFiles} userId={userId}/>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
