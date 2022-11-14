import { useCallback, useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import "./App.css";
import Navigation from "./components/Navigation/Navigation";
import UploadFile from "./components/UploadFile/UploadFile";
import Preview from "./components/Preview/Preview";
import Download from "./components/Download/Download";
import Login from "./components/Login/Login";
import Register from './components/Register/Register';
import History from "./components/History/History";
import { Footer } from "./components/Footer";
import { About } from "./components/About";
import { Logout } from "./components/Logout";
import { NotFound } from "./components/NotFound";
import User from "./UserInterface";
import useFetchJSON from "./useFetchJSON";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [data, error] = useFetchJSON<User>('/api/login');

  useEffect(() => {
    if (error) {
      setUser(null);
    } else {
      setUser(data);
    }
  }, [data, error])

  const handleSetUser = useCallback((user: User) => {
    setUser(user);
  }, []);

  return (
    <>
      <Navigation user={user} />
      <div className="main">
        <Routes>
          <Route path="/" element={<UploadFile />} />
          <Route path="/preview/:fileId" element={<Preview />} />
          <Route path="/download/:fileId" element={<Download />} />
          <Route path='/login' element={<Login setUser={handleSetUser} />} />
          <Route path='/register' element={<Register />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/history" element={<History />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
    </>
  );
}
