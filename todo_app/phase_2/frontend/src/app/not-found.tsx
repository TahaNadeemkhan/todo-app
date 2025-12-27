import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="flex h-screen flex-col items-center justify-center space-y-4">
      <h2 className="text-xl font-bold">404 - Not Found</h2>
      <p>Could not find requested resource</p>
      <Button asChild>
        <Link href="/dashboard">Return Home</Link>
      </Button>
    </div>
  )
}
