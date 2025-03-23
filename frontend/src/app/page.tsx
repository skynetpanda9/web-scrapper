import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Fetch data from backend
async function getSummaries() {
  const res = await fetch("http://localhost:5001/summaries", {
    cache: "no-store", // Fresh data har baar
  });
  if (!res.ok) throw new Error("Failed to fetch summaries");
  return res.json();
}

export default async function Home() {
  const summaries = await getSummaries();

  return (
    <div className='container mx-auto p-4'>
      <h1 className='text-3xl font-bold mb-6 text-center'>
        Tech News Summaries
      </h1>
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
        {summaries.map(
          (article: { title: string; url: string; summary: string }) => (
            <Card
              key={article.url}
              className='shadow-lg hover:shadow-xl transition-shadow'
            >
              <CardHeader>
                <CardTitle className='text-xl'>{article.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className='text-gray-700 mb-4'>{article.summary}</p>
                <a
                  href={article.url}
                  target='_blank'
                  rel='noopener noreferrer'
                  className='text-blue-500 hover:underline'
                >
                  Read Full Article
                </a>
              </CardContent>
            </Card>
          )
        )}
      </div>
    </div>
  );
}
