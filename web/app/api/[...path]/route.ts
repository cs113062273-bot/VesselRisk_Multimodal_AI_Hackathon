import { NextRequest } from 'next/server';

export const dynamic='force-dynamic';
const allowed=new Set(['health','schema','cases','model-info','evidence','predict','explain','report']);

async function proxy(request:NextRequest,context:{params:Promise<{path:string[]}>}){
  const {path}=await context.params;
  if(path.length!==1||!allowed.has(path[0]))return Response.json({detail:'Unknown model service endpoint'},{status:404});
  try{
    const base=process.env.API_URL||'http://127.0.0.1:8000';
    const upstream=await fetch(`${base}/${encodeURIComponent(path[0])}`,{
      method:request.method,headers:{'Content-Type':'application/json'},
      body:request.method==='POST'?await request.text():undefined,
      cache:'no-store',signal:AbortSignal.timeout(85000),
    });
    return new Response(upstream.body,{status:upstream.status,headers:{'Content-Type':upstream.headers.get('Content-Type')||'application/json','Cache-Control':'no-store'}});
  }catch{
    return Response.json({detail:'The clinical model service is unavailable. Start both services and retry.'},{status:503});
  }
}
export {proxy as GET,proxy as POST};
