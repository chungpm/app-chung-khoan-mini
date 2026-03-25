import streamlit as st
import re
import yfinance as yf
import pandas as pd
import requests
import time
# CHỈ IMPORT ĐÚNG TRADING ĐỂ LẤY BẢNG GIÁ CƠ SỞ (Đã test thành công)
from vnstock import Trading

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Bảng Giá Cá Nhân", layout="wide")
st.title("📈 Bảng Theo Dõi Tài Chính Của Chung")

# --- 2. VĨ MÔ QUỐC TẾ & CHỈ SỐ VN ---
st.subheader("🌐 Vĩ mô Quốc tế & Chỉ số VN")

if st.button("🔄 Cập nhật Vĩ mô"):
    try:
        # LUỒNG 1: Hàm lấy 5 Chỉ số VN (Bắn thẳng API TradingView của VNDirect, siêu mượt)
        def get_vn_indices(ticker):
            result = {'current_price': 0.0, 'last_price': 0.0}
            try:
                now = int(time.time())
                past = now - 15 * 86400 # Quét mẻ lưới 15 ngày
                
                # Map đúng tên chuẩn mà hệ thống VNDirect đang dùng
                sym_map = {
                    'VNINDEX': 'VNINDEX',
                    'HNXINDEX': 'HNX',
                    'UPCOMINDEX': 'UPCOM',
                    'VN30': 'VN30',
                    'HNX30': 'HNX30'
                }
                mapped_sym = sym_map.get(ticker, ticker)
                
                url = f"https://dchart-api.vndirect.com.vn/dchart/history?symbol={mapped_sym}&resolution=D&from={past}&to={now}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=5).json()
                
                if res.get('s') == 'ok' and 'c' in res:
                    if len(res['c']) >= 2:
                        result['current_price'] = float(res['c'][-1])
                        result['last_price'] = float(res['c'][-2])
                    elif len(res['c']) == 1:
                        result['current_price'] = float(res['c'][0])
                        result['last_price'] = float(res['c'][0])
            except:
                pass
            return result

        # LUỒNG 2: Hàm lấy Quốc tế (Dùng Yahoo Finance)
        def get_global_prices(ticker):
            result = {'current_price': 0.0, 'last_price': 0.0}
            try:
                t = yf.Ticker(ticker)
                try:
                    result['current_price'] = float(t.fast_info['lastPrice'])
                except: pass
                    
                try:
                    hist = t.history(period="5d")
                    if not hist.empty:
                        if result['current_price'] == 0.0:
                            result['current_price'] = float(hist['Close'].iloc[-1])
                        if len(hist) > 1:
                            result['last_price'] = float(hist['Close'].iloc[-2])
                        else:
                            result['last_price'] = float(hist['Close'].iloc[-1])
                except: pass
            except: pass
            return result
            
        # Kéo dữ liệu 5 chỉ số VN
        vni_data = get_vn_indices('VNINDEX')
        hnx_data = get_vn_indices('HNXINDEX')
        upcom_data = get_vn_indices('UPCOMINDEX')
        vn30_data = get_vn_indices('VN30')
        hnx30_data = get_vn_indices('HNX30')
        
        # Kéo dữ liệu 4 chỉ số Quốc tế
        vang_data = get_global_prices('GC=F')
        dau_data = get_global_prices('CL=F')
        usd_data = get_global_prices('VND=X')
        caosu_data = get_global_prices('TRB=F')
        
        # Hàm vẽ thông số lên màn hình
        def render_metric(col, title, data, fmt):
            if data['current_price'] > 0:
                col.metric(title, fmt.format(data['current_price']))
            elif data['last_price'] > 0:
                col.metric(title, fmt.format(data['last_price']) + " (*)")
            else:
                col.metric(title, "N/A")

        # Hiển thị Hàng 1: Chứng khoán VN
        st.markdown("**🇻🇳 Chỉ số Chứng khoán Việt Nam**")
        c1, c2, c3, c4, c5 = st.columns(5)
        render_metric(c1, "VN-INDEX", vni_data, "{:,.2f}")
        render_metric(c2, "HNX-INDEX", hnx_data, "{:,.2f}")
        render_metric(c3, "UPCOM", upcom_data, "{:,.2f}")
        render_metric(c4, "VN30", vn30_data, "{:,.2f}")
        render_metric(c5, "HNX30", hnx30_data, "{:,.2f}")

        # Hiển thị Hàng 2: Hàng hóa Quốc tế
        st.markdown("**🌍 Hàng hóa & Tỷ giá Quốc tế**")
        g1, g2, g3, g4 = st.columns(4)
        render_metric(g1, "Vàng Thế giới", vang_data, "${:,.1f}")
        render_metric(g2, "Dầu WTI", dau_data, "${:,.2f}")
        render_metric(g3, "USD/VND (Bank)", usd_data, "{:,.0f} đ")
        render_metric(g4, "Cao su (Tokyo)", caosu_data, "¥{:,.1f}")
            
        # --- BẢNG COPY DATA DÀNH CHO AI ---
        quoc_te_data = [
            {"symbol": "VNINDEX", "name": "Chi so VN-Index", "current_price": vni_data['current_price'], "last_price": vni_data['last_price'], "unit": "Point"},
            {"symbol": "HNXINDEX", "name": "Chi so HNX-Index", "current_price": hnx_data['current_price'], "last_price": hnx_data['last_price'], "unit": "Point"},
            {"symbol": "UPCOMINDEX", "name": "Chi so UPCOM-Index", "current_price": upcom_data['current_price'], "last_price": upcom_data['last_price'], "unit": "Point"},
            {"symbol": "VN30", "name": "Chi so VN30", "current_price": vn30_data['current_price'], "last_price": vn30_data['last_price'], "unit": "Point"},
            {"symbol": "HNX30", "name": "Chi so HNX30", "current_price": hnx30_data['current_price'], "last_price": hnx30_data['last_price'], "unit": "Point"},
            {"symbol": "GOLD", "name": "Vang The Gioi", "current_price": vang_data['current_price'], "last_price": vang_data['last_price'], "unit": "USD/oz"},
            {"symbol": "OIL_WTI", "name": "Dau WTI", "current_price": dau_data['current_price'], "last_price": dau_data['last_price'], "unit": "USD/barrel"},
            {"symbol": "USD_VND", "name": "Ty gia Ngan hang", "current_price": usd_data['current_price'], "last_price": usd_data['last_price'], "unit": "VND"},
            {"symbol": "RUBBER_TK", "name": "Cao su Tokyo", "current_price": caosu_data['current_price'], "last_price": caosu_data['last_price'], "unit": "JPY/kg"}
        ]
        
        df_qt = pd.DataFrame(quoc_te_data)
        csv_qt = df_qt.to_csv(index=False)
        
        st.info("📋 Nút Copy Data Vĩ Mô:")
        st.code(csv_qt, language="csv")
        
    except Exception as e:
        st.warning(f"Lỗi tải Vĩ mô: {e}")

st.divider()

# --- 3. CHỨNG KHOÁN VIỆT NAM ---
st.subheader("📊 Danh mục Cổ phiếu (Cơ sở)")

@st.cache_resource
def get_trading_engine():
    return Trading(source='KBS')

trading = get_trading_engine()

input_ma = st.text_input(
    "Nhập danh sách mã cổ phiếu (cách nhau bởi dấu phẩy):", 
    "VCB, CTG, TCB, EIB, SSI, VND, VHM, VIC, HPG, MWG, FPT, MSN, GVR, BSR, GAS, PLX, BVH"
)

if st.button("🚀 Lấy Dữ Liệu VN"):
    try:
        # Lọc Regex chống lỗi điện thoại
        list_ma = [re.sub(r'[^a-zA-Z0-9]', '', s).upper() for s in input_ma.split(',')]
        list_ma = [s for s in list_ma if s]
        
        data = trading.price_board(list_ma)
        
        if data is not None and not data.empty:
            st.success("Lấy dữ liệu thành công!")
            st.dataframe(data, use_container_width=True)
            
            csv_string = data.to_csv(index=False)
            st.info("📋 Nút Copy Data VN: Chạm vào biểu tượng [Copy] ở góc phải ô đen dưới đây:")
            st.code(csv_string, language="csv")
            
        else:
            st.warning("Không có dữ liệu trả về. Bảng giá có thể đang bảo trì.")
            
    except Exception as e:
        import traceback
        st.error("Rất tiếc, hệ thống gặp sự cố!")
        st.code(traceback.format_exc(), language="text")