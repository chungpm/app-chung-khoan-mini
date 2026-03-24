import streamlit as st
from vnstock import Trading # IMPORT TRỰC TIẾP CLASS TRADING

# Cấu hình giao diện web
st.set_page_config(page_title="Bảng Giá Cá Nhân", layout="wide")
st.title("📈 Bảng Theo Dõi Cổ Phiếu Của Chung")

# Khởi tạo thư viện theo chuẩn Agent Guide
@st.cache_resource
def get_trading_engine():
    # Khai báo trực tiếp nguồn dữ liệu (KBS hoặc VCI đang hoạt động ổn định nhất)
    return Trading(source='KBS')

# Lấy "động cơ" giao dịch
trading = get_trading_engine()

# Ô nhập mã cổ phiếu (đã điền sẵn các mã quen thuộc trong danh mục)
input_ma = st.text_input(
    "Nhập danh sách mã cổ phiếu (cách nhau bởi dấu phẩy):", 
    "GVR, SSI, BVH, TCB, EIB, GAS, BSR, PLX"
)

if st.button("Lấy Dữ Liệu"):
    try:
        # Làm sạch danh sách mã nhập vào thành List
        list_ma = [s.strip().upper() for s in input_ma.split(',')]
        
        # CÚ PHÁP MỚI: Truyền thẳng danh sách (List) vào hàm price_board
        data = trading.price_board(list_ma)
        
        if data is not None and not data.empty:
            st.success("Lấy dữ liệu thành công!")
            
            # Hiển thị dữ liệu lên giao diện web để bạn xem
            st.dataframe(data, use_container_width=True)
            
            # TẠO TÍNH NĂNG COPY DATA NHANH
            # Chuyển bảng dữ liệu thành chuỗi văn bản định dạng CSV (bỏ cột số thứ tự index)
            csv_string = data.to_csv(index=False)
            
            st.info("📋 Nút Copy Data: Chạm vào biểu tượng [Copy] ở góc phải ô đen dưới đây để chép dữ liệu và gửi cho tôi:")
            # Bỏ chuỗi CSV vào khung code để lấy nút Copy
            st.code(csv_string, language="csv")
            
        else:
            st.warning("Không có dữ liệu trả về. Bảng giá có thể đang bảo trì.")
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc() # Lấy toàn bộ gốc rễ của lỗi
        
        st.error("Rất tiếc, hệ thống gặp sự cố!")
        st.info("👇 Sếp hãy nhấn vào biểu tượng [Copy] ở góc trên bên phải của ô đen dưới đây và dán thẳng vào chat cho tôi nhé:")
        
        # Lệnh st.code tự động tạo ra nút Copy cực kỳ tiện lợi
        st.code(error_detail, language="text")
        
        # Tùy chọn: Nếu bạn muốn copy cả danh sách mã đang nhập để tôi test thử
        st.write("Dữ liệu đầu vào lúc báo lỗi:")
        st.code(f"Mã: {input_ma}", language="text")