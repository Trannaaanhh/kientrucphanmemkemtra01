import sys

with open('d:/TheGioiLapTrinh/kiemtra01/frontend/src/app/pages/CustomerDashboard.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the combined ternary back into two separate 'if' blocks, each with its own header.
header_jsx = """<div className="min-h-screen bg-slate-50 page-enter">
        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <ShoppingCart className="w-7 h-7 text-blue-500" />
                <h1 className="text-xl font-bold">Cửa Hàng Điện Tử</h1>
                {getUserName() && (
                  <span className="hidden sm:inline text-sm text-slate-500">
                    Xin chào, <span className="font-medium text-slate-700">{getUserName()}</span>
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <Link to="/customer/login">
                  <Button variant="ghost" onClick={clearAuth}>
                    <LogOut className="w-5 h-5 mr-2" />
                    Đăng Xuất
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 py-8 flex flex-col items-center">"""

start_shipping = content.find('<div className="w-full max-w-2xl pt-4">')
if start_shipping == -1:
    print('shipping start not found')
    sys.exit(1)

end_shipping = content.find('          ) : (', start_shipping)
if end_shipping == -1:
    print('shipping end not found')
    sys.exit(1)

shipping_jsx = content[start_shipping:end_shipping]

start_done = content.find('<div className="w-full max-w-lg pt-4">', end_shipping)
if start_done == -1:
    print('done start not found')
    sys.exit(1)

end_done = content.find('          )}\\n        </main>', start_done)
if end_done == -1:
    # Try alternate find just in case
    end_done = content.find('          )}\\r\\n        </main>', start_done)
if end_done == -1:
    print('done end not found')
    sys.exit(1)

done_jsx = content[start_done:end_done]

start_block = content.find('  // ── SHIPPING & DONE SCREENS ─────────────────────────────────')
end_block = content.find('  // ── MAIN SHOP SCREEN ────────────────────────────────────────')

new_block = f"""  // ── SHIPPING FORM SCREEN ────────────────────────────────────
  if (flowStep === 'shipping') {{
    return (
      {header_jsx}
{shipping_jsx}        </main>
      </div>
    );
  }}

  // ── ORDER COMPLETE SCREEN ───────────────────────────────────
  if (flowStep === 'done') {{
    return (
      {header_jsx}
{done_jsx}        </main>
      </div>
    );
  }}

"""

content = content[:start_block] + new_block + content[end_block:]

with open('d:/TheGioiLapTrinh/kiemtra01/frontend/src/app/pages/CustomerDashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Rewrite successful')
