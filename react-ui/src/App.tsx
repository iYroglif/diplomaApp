import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import "./App.css";
import Navigation from "./components/Navigation/Navigation";
import UploadFile from "./components/UploadFile/UploadFile";
import Preview from "./components/Preview/Preview";
import Download from "./components/Download/Download";
import { Login } from './components/Login';
import { Register } from './components/Register';
import { HistoryComponent } from "./components/HistoryComponent"
import { Footer } from "./components/Footer";
import { About } from "./components/About";
import { Logout } from "./components/Logout";
import { NotFound } from "./components/NotFound";
import User from "./UserInterface";

export default function App() {
  const [user, setUser] = useState<User | null>(null);

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
