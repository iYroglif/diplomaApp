import { useEffect, useState } from "react"
import { Navigate } from "react-router-dom"

export const Logout = () => {
    const [isLogout, setIsLogout] = useState(false)

    useEffect(() => {
        fetch('/api/logout').then(() => setIsLogout(true))
    }, [])

    return (
        <>
            {isLogout ? (
                <Navigate replace to='/' />
            ) : (
                <p>Производится выход...</p>
            )}
        </>
    )
}