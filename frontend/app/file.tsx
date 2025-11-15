"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { InputGroup } from "@/components/ui/input-group";

export default function FileInfo({file, i, api, userId, setFiles}: {file: string, i:number, userId: number, api: Function, setFiles: Function}) {
  let data = JSON.parse(file);

  const downloadFile = async () => {
    // Implement download file logic here
  };

  const shareFile = async (e: any) => {
    const userInput = document.getElementById(`${i}-user`) as HTMLInputElement;
    const username = userInput.value;
    if (!username) {
      alert("Please enter a username to share the file with.");
      return;
    }

    // {"status": "File shared", "shared_with": target_username}
    const resp = await api(`/api/share/${data["id"]}?target_username=${username}`, {
      method: "POST",
    });
    alert(`File shared with ${resp["shared_with"]}`);
  };

  const deleteFile = async () => {
    api(`/api/file/${data["id"]}`, {
      method: "DELETE",
    }    
    );
    const data2 = await api("/api/list_files");
    setFiles(data2["files"] || []);
  };

  const getName = () => {
    console.log(userId, Number(data["original"]));
    if (userId === Number(data["original"])) {
      return <span>{data["filename"]}</span>
    }
    else {
      return <span>{data["filename"]} (shared by (unable to resolve))</span>
    }
  };

  return <div className="grid grid-cols-2 gap-6 items-baseline p-4">
      {getName()}
      <InputGroup className="grid grid-cols-4 gap-2 border-0">
        <Button onClick={downloadFile} className="bg-green-500">Download</Button>
        <Button onClick={deleteFile} className="bg-red-500" hidden={userId === Number(data["original"]) ? false : true}>Delete</Button>
        <Button id={`${i}-share`} onClick={shareFile} hidden={userId === Number(data["original"]) ? false : true}>Share</Button>
        <Input id={`${i}-user`} placeholder="Username" hidden={userId === Number(data["original"]) ? false : true}></Input>
      </InputGroup>
  </div>;
};