import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import AuthLayout from '../components/layout/AuthLayout';

export default function LoginPage() {
  const navigate = useNavigate();
  const { error, success } = useToast();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await login(email, password);
      success('Login successful');
      navigate('/');
    } catch (err) {
      error(err?.message || 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      heroTitle="Empowering Blog Writing Through AI"
      heroDescription="Generate authentic, engaging blog posts with AI-powered writing. Choose your style, enter a topic, and let AI do the rest."
      featurePoints={[
        'Secure account-based blog ownership',
        'Public share links with helpful feedback tracking',
      ]}
      formTitle="Sign in to your account"
      formDescription="Login to generate blogs, manage posts, and track analytics."
      footer={(
        <>
          New user?{' '}
          <Link to="/register" className="text-primary-300 hover:text-primary-200 hover:underline">
            Create account
          </Link>
        </>
      )}
    >
      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <div>
          <label className="block text-sm font-semibold text-primary-100 mb-2">Email address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="you@example.com"
            className="w-full rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-primary-100/50 focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-primary-100 mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            placeholder="Enter your password"
            className="w-full rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-primary-100/50 focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>

        <Button type="submit" isLoading={isSubmitting} className="w-full rounded-2xl py-3 text-lg">
          Sign in
        </Button>
      </form>
    </AuthLayout>
  );
}
