import { Link } from "react-router-dom"

export default function Dashboard() {
    return (
        <div className="p-8">
            <h1 className="text-4xl font-bold">This is your dashboard</h1>

            <div className="mt-4">
                <Link to="/home" className="text-blue-500 hover:underline">
                    Go to Home Page
                </Link>
            </div>

            <div className="mt-4">
                <Link to="/login" className="text-blue-500 hover:underline">
                    Go to Login Page
                </Link>
            </div>
        </div>
    );
}