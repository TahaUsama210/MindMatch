import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Welcome to MindMatch</h1>
      <p className="mt-2 text-gray-500">
        Your personalized task automator.
      </p>

        <div className="mt-6">
            <Link to="/login" className="text-blue-500 hover:underline">
                Go to Login Page
            </Link>
        </div>

        <div className="mt-4">  
            <Link to="/dashboard" className="text-blue-500 hover:underline">
                Go to Dashboard
            </Link>
        </div>
    </div>
    
  );
}
