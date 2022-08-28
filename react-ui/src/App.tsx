import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { UploadFile } from "./components/UploadFile";
import { Navigation } from "./components/Navigation";
import { Login } from './components/Login';
import { Register } from './components/Register';
import { HistoryComponent } from "./components/HistoryComponent"
import { Footer } from "./components/Footer";
import { About } from "./components/About";
import "./App.css"
import { Logout } from "./components/Logout";
import { Preview } from "./components/main/Preview";
import { Download } from "./components/main/Download";
import { NotFound } from "./components/NotFound";

export interface IUser {
  username: string
}

export const App = () => {
  const [user, setUser] = useState<IUser | null>(null)

  useEffect(() => {
    fetch('/api/login')
      .then((res) => {
        if (res.ok)
          return res.json()
      }).then((data) => setUser(data))
  }, [])

  return (
    <>
      <Navigation user={user} />
      <div className="main">
        <Routes>
          <Route path="/" element={<UploadFile />} />
          <Route path="/preview/:fileId" element={<Preview />} />
          <Route path="/download/:fileId" element={<Download />} />
          <Route path='/login' element={<Login />} />
          <Route path='/register' element={<Register />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/history" element={<HistoryComponent />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
    </>
  );
}
